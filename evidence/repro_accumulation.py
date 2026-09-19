"""CPU-only diagnostic of ERABI's *actual uploaded* run_full_training function.

No GLiClass imports, weights, GPUs, or downloads. Uses AST to load only
run_full_training and Trainer.compute_batch_loss, replacing model/optimizer/
evaluation and shuffle with tiny deterministic test doubles. The original
accumulation arithmetic and optimizer-step boundaries execute unchanged.

Usage:
  python repro_accumulation.py --source src/erabi/train.py --out audit/accumulation

This is a review probe, not a training framework or a real-model benchmark.
It executes the two named function bodies: use only with reviewed/trusted code.
"""
from __future__ import annotations
import argparse, ast, contextlib, difflib, hashlib, io, json, os, tempfile, time, types
from pathlib import Path
import torch
import torch.nn.functional as F

OLD = '''            # Determine actual window size for this accumulation window (handles fractional tail)
            window_offset = batch_idx % trainer.gradient_accumulation_steps
            remaining_in_window = trainer.gradient_accumulation_steps - window_offset
            remaining_in_epoch = total_micro_batches - batch_idx
            current_window_size = min(remaining_in_window, remaining_in_epoch)

            loss = trainer.compute_batch_loss(tokenized, target_indices, num_choices_list, max_num_classes)
            loss_scaled = loss / current_window_size'''
NEW = '''            # Weight each microbatch mean by its sample share in this optimizer window.
            # The window denominator is constant until optimizer.step(), including the tail.
            window_start_batch = (batch_idx // trainer.gradient_accumulation_steps) * trainer.gradient_accumulation_steps
            window_start_sample = window_start_batch * batch_size
            window_end_sample = min(
                window_start_sample + trainer.gradient_accumulation_steps * batch_size,
                len(epoch_records),
            )
            window_sample_count = window_end_sample - window_start_sample

            loss = trainer.compute_batch_loss(tokenized, target_indices, num_choices_list, max_num_classes)
            loss_scaled = loss * (len(batch_records) / window_sample_count)'''


def functions_from_source(source, filename):
    tree=ast.parse(source)
    full=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='run_full_training')
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Trainer')
    loss=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='compute_batch_loss')
    module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),loss,full],type_ignores=[])
    ast.fix_missing_locations(module)
    ns={'argparse':argparse,'os':os,'json':json,'time':time,'torch':torch,'F':F}
    exec(compile(module,str(filename),'exec'),ns)
    return ns


class NoShuffle:
    def shuffle(self, value):
        pass


class TinyModel(torch.nn.Module):
    def __init__(self):
        super().__init__();self.weight=torch.nn.Parameter(torch.tensor(0.,dtype=torch.float64))
    def forward(self,x,max_num_classes=2):
        s=self.weight*x
        return types.SimpleNamespace(logits=torch.stack((s,torch.zeros_like(s)),dim=-1))


class CaptureOptimizer:
    def __init__(self,model):self.model=model;self.gradients=[]
    def zero_grad(self):self.model.zero_grad(set_to_none=True)
    def step(self):
        self.gradients.append(float(self.model.weight.grad.item()))
        # Do not update: each comparison measures gradients at the same parameter values.


def execute(source, rows, micro, accum):
    ns=functions_from_source(source,'reviewed_train.py')
    actual_loss=ns['compute_batch_loss']; created=[]
    class TinyTrainer:
        def __init__(self,**kw):
            self.model=TinyModel();self.optimizer=CaptureOptimizer(self.model)
            self.device='cpu';self.micro_batch_size=kw['micro_batch_size'];self.gradient_accumulation_steps=kw['gradient_accumulation_steps'];self.max_norm=1e12
            created.append(self)
        def prepare_batch(self,batch_records,**kw):
            x=torch.tensor([r['x'] for r in batch_records],dtype=torch.float64)
            y=[r['y'] for r in batch_records]
            return {'x':x},y,[2]*len(y),2
        def compute_batch_loss(self,*args):return actual_loss(self,*args)
        def evaluate(self,records):
            return {'accuracy':0.,'mean_nll':1.,'mean_brier':1.,'pair_metrics':{'both_correct_rate':0.,'both_correct_pairs':0,'total_pairs':1}}
        def save_checkpoint(self,out):Path(out).mkdir(parents=True,exist_ok=True)
    ns['Trainer']=TinyTrainer;ns['random']=types.SimpleNamespace(Random=lambda seed:NoShuffle())
    with tempfile.TemporaryDirectory(prefix='erabi_cpu_grad_') as tmp:
        path=Path(tmp);(path/'out').mkdir()
        for name,records in [('train',rows),('dev',rows[:2])]:
            (path/f'{name}.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
        args=argparse.Namespace(data_dir=tmp,output_dir=str(path/'out'),model_id='synthetic_cpu_model',device='cpu',lr=2e-5,weight_decay=.01,seed=42,micro_batch_size=micro,gradient_accumulation_steps=accum,epochs=1)
        with contextlib.redirect_stdout(io.StringIO()):ns['run_full_training'](args)
    return created[0].optimizer.gradients


def reference(rows,micro,accum):
    gradients=[]
    for start in range(0,len(rows),micro*accum):
        batch=rows[start:start+micro*accum];model=TinyModel()
        x=torch.tensor([r['x'] for r in batch],dtype=torch.float64);y=torch.tensor([r['y'] for r in batch],dtype=torch.long)
        F.cross_entropy(model(x).logits.float(),y).backward()
        gradients.append(float(model.weight.grad.item()))
    return gradients


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    torch.set_num_threads(1)
    source=a.source.read_text(encoding='utf-8');a.out.mkdir(parents=True,exist_ok=True)
    if source.count(OLD)!=1:raise SystemExit('Expected reviewed M3.3 scaling block not found exactly once. No automatic change made.')
    fixed=source.replace(OLD,NEW).replace('        total_micro_batches = (len(epoch_records) + batch_size - 1) // batch_size\n','')
    special=[{'x':2.,'y':1} for _ in range(14)]+[{'x':4.,'y':0} for _ in range(2)]
    generic=lambda n:[{'x':float((i%7)+1),'y':int(i%3!=0)} for i in range(n)]
    cases=[('direction_flip_full16',special,2,8),('partial8',generic(8),2,8),('short_last_micro15',generic(15),2,8),('full_then_tail23',generic(23),2,8),('accum_one5',generic(5),2,1)]
    results=[]
    for name,rows,micro,accum in cases:
        ref=reference(rows,micro,accum);before=execute(source,rows,micro,accum);after=execute(fixed,rows,micro,accum)
        error=lambda vals:max(abs(x-y) for x,y in zip(vals,ref)) if len(vals)==len(ref) else float('inf')
        result={'case':name,'samples':len(rows),'micro_batch':micro,'accum':accum,'reference_grads':ref,'uploaded_loop_grads':before,'patched_loop_grads':after,'uploaded_max_error':error(before),'patched_max_error':error(after)}
        assert result['patched_max_error']<1e-6
        results.append(result)
    output={'source':str(a.source),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'torch':torch.__version__,'scope':'CPU synthetic gradient check, not actual-model retraining; real source function and loss executed with tiny dependencies. Clipping nonbinding; no optimizer update; no shuffle/dropout.','cases':results,'full_window_wrong_divisors':list(range(8,0,-1)),'correct_full_window_micro_weights':[1/8]*8,'wrong_sum_micro_weights':sum(1/i for i in range(1,9))}
    (a.out/'gradient_probe.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    patch=''.join(difflib.unified_diff(source.splitlines(keepends=True),fixed.splitlines(keepends=True),fromfile='a/src/erabi/train.py',tofile='b/src/erabi/train.py'))
    (a.out/'gradient_accumulation_fix.patch').write_text(patch,encoding='utf-8')
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()
