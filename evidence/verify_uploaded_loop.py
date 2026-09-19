"""Execute reviewed training/loss source on synthetic CPU data, without model downloads.
Use: python verify_uploaded_loop.py --source src/erabi/train.py --out gradient_check.json
The model, input preparation, shuffle, evaluation and optimizer are test doubles.
The uploaded run_full_training and compute_batch_loss bodies execute unmodified.
Optimizer records gradients at each step; it does not update parameters.
No claim of reproducing a GLiClass training run.
"""
from __future__ import annotations
import argparse,ast,contextlib,hashlib,io,json,os,tempfile,time,types
from pathlib import Path
import torch
import torch.nn.functional as F

def functions_from_source(source, filename):
    tree = ast.parse(source)
    full = next((x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'run_full_training'))
    cls = next((x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Trainer'))
    loss = next((x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == 'compute_batch_loss'))
    module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), loss, full], type_ignores=[])
    ast.fix_missing_locations(module)
    ns = {'argparse': argparse, 'os': os, 'json': json, 'time': time, 'torch': torch, 'F': F}
    exec(compile(module, str(filename), 'exec'), ns)
    return ns

class NoShuffle:

    def shuffle(self, value):
        pass

class TinyModel(torch.nn.Module):

    def __init__(self):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.tensor(0.0, dtype=torch.float64))

    def forward(self, x, max_num_classes=2):
        s = self.weight * x
        return types.SimpleNamespace(logits=torch.stack((s, torch.zeros_like(s)), dim=-1))

class CaptureOptimizer:

    def __init__(self, model):
        self.model = model
        self.gradients = []

    def zero_grad(self):
        self.model.zero_grad(set_to_none=True)

    def step(self):
        self.gradients.append(float(self.model.weight.grad.item()))

def execute(source, rows, micro, accum):
    ns = functions_from_source(source, 'reviewed_train.py')
    actual_loss = ns['compute_batch_loss']
    created = []

    class TinyTrainer:

        def __init__(self, **kw):
            self.model = TinyModel()
            self.optimizer = CaptureOptimizer(self.model)
            self.device = 'cpu'
            self.micro_batch_size = kw['micro_batch_size']
            self.gradient_accumulation_steps = kw['gradient_accumulation_steps']
            self.max_norm = 1000000000000.0
            created.append(self)

        def prepare_batch(self, batch_records, **kw):
            x = torch.tensor([r['x'] for r in batch_records], dtype=torch.float64)
            y = [r['y'] for r in batch_records]
            return ({'x': x}, y, [2] * len(y), 2)

        def compute_batch_loss(self, *args):
            return actual_loss(self, *args)

        def evaluate(self, records):
            return {'accuracy': 0.0, 'mean_nll': 1.0, 'mean_brier': 1.0, 'pair_metrics': {'both_correct_rate': 0.0, 'both_correct_pairs': 0, 'total_pairs': 1}}

        def save_checkpoint(self, out):
            Path(out).mkdir(parents=True, exist_ok=True)
    ns['Trainer'] = TinyTrainer
    ns['random'] = types.SimpleNamespace(Random=lambda seed: NoShuffle())
    with tempfile.TemporaryDirectory(prefix='erabi_cpu_grad_') as tmp:
        path = Path(tmp)
        (path / 'out').mkdir()
        for name, records in [('train', rows), ('dev', rows[:2])]:
            (path / f'{name}.jsonl').write_text(''.join((json.dumps(r) + '\n' for r in records)))
        args = argparse.Namespace(data_dir=tmp, output_dir=str(path / 'out'), model_id='synthetic_cpu_model', device='cpu', lr=2e-05, weight_decay=0.01, seed=42, micro_batch_size=micro, gradient_accumulation_steps=accum, epochs=1)
        with contextlib.redirect_stdout(io.StringIO()):
            ns['run_full_training'](args)
    return created[0].optimizer.gradients

def reference(rows, micro, accum):
    gradients = []
    for start in range(0, len(rows), micro * accum):
        batch = rows[start:start + micro * accum]
        model = TinyModel()
        x = torch.tensor([r['x'] for r in batch], dtype=torch.float64)
        y = torch.tensor([r['y'] for r in batch], dtype=torch.long)
        F.cross_entropy(model(x).logits.float(), y).backward()
        gradients.append(float(model.weight.grad.item()))
    return gradients

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();torch.set_num_threads(1)
    source=a.source.read_text(encoding='utf-8')
    special=[{'x':2.,'y':1} for _ in range(14)]+[{'x':4.,'y':0} for _ in range(2)]
    generic=lambda n:[{'x':float((i%7)+1),'y':int(i%3!=0)} for i in range(n)]
    cases=[('normal16',special,2,8),('partial8',generic(8),2,8),('odd15',generic(15),2,8),('multi23',generic(23),2,8),('accum_one5',generic(5),2,1)]
    out=[]
    for name,rows,micro,accum in cases:
        ref=reference(rows,micro,accum);got=execute(source,rows,micro,accum)
        if len(ref)!=len(got):raise AssertionError('optimizer step count mismatch')
        err=max(abs(x-y) for x,y in zip(ref,got))
        if err>=1e-6:raise AssertionError(f'{name}: {err}')
        out.append({'case':name,'reference':ref,'actual_uploaded_loop':got,'max_abs_error':err})
    res={'scope':__doc__,'torch':torch.__version__,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':out}
    a.out.parent.mkdir(exist_ok=True,parents=True)
    a.out.write_text(json.dumps(res,indent=2),encoding='utf-8')
    print(json.dumps(res,indent=2))

if __name__=='__main__': main()
