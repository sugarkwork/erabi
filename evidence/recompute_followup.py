"""Recompute archived ERABI predictions. Standard-library only; no model loading.
Usage: python recompute_followup.py --root PATH_TO_EXTRACTED_BUNDLE --out OUTPUT_DIR
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, unicodedata
from pathlib import Path
from collections import defaultdict, Counter


def load(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def norm(text):
    return unicodedata.normalize('NFC', text).strip().lower()


def fp(row):
    return json.dumps([norm(row['context']),norm(row['question']),sorted(norm(c['text']) for c in row['choices'])],ensure_ascii=False)


def metrics(rows, predictions):
    lookup = {p['id']:p for p in predictions}
    assert len(lookup)==len(predictions)==len(rows)
    assert set(lookup)=={r['id'] for r in rows}
    correct=nll=brier=0.; group=defaultdict(list); tasks=defaultdict(lambda: [0,0]); nbad=0
    for r in rows:
        p=lookup[r['id']]; ids=[c['id'] for c in r['choices']]; pi=[c['id'] for c in p['choices']]
        assert ids==pi and r['target']['choice_id']==p['target']
        z=p['raw_logits']; k=len(ids); assert len(z)==k and all(math.isfinite(x) for x in z)
        mx=max(z); logsum=mx+math.log(sum(math.exp(x-mx) for x in z)); prob=[math.exp(x-logsum) for x in z]
        assert max(abs(a-c['probability']) for a,c in zip(prob,p['choices']))<1e-6
        best=ids[max(range(k), key=z.__getitem__)]; assert best==p['best_candidate_id']
        y=ids.index(r['target']['choice_id']); ok=(best==ids[y]); assert ok==p['is_correct']
        correct+=ok; nll+=logsum-z[y]; brier+=sum((x-int(i==y))**2 for i,x in enumerate(prob))
        task=r.get('rule_kind') or r['task_family']; tasks[task][0]+=ok;tasks[task][1]+=1
        group[r['group_id']].append((r,p))
    pairs=defaultdict(lambda:dict(groups=0,both_correct=0,same_prediction=0,different_prediction=0))
    for gid,pair in group.items():
        if len(pair)!=2: continue
        same=pair[0][0]['target']['choice_id']==pair[1][0]['target']['choice_id']
        key='same_target' if same else 'different_target'
        task=pair[0][0].get('rule_kind') or pair[0][0]['task_family']
        for label in (key,key+'/'+task):
            d=pairs[label]; d['groups']+=1;d['both_correct']+=all(x[1]['is_correct'] for x in pair)
            psame=pair[0][1]['best_candidate_id']==pair[1][1]['best_candidate_id']
            d['same_prediction']+=psame;d['different_prediction']+=not psame
    n=len(rows)
    return dict(count=n,correct=int(correct),accuracy=correct/n,nll=nll/n,brier=brier/n,
                tasks={k:dict(correct=v[0],count=v[1]) for k,v in tasks.items()},pairs=dict(pairs))


def semantic_key(row):
    # Limited diagnostic: only the explicit-rule family whose numeric states are unambiguous.
    kind=row.get('rule_kind')
    if kind=='composite_logic':
        hp=int(re.search(r'HPは(\d+)',row['context']).group(1))
        threshold=int(re.search(r'HPが(\d+)',row['question']).group(1))
        return ('composite_logic',hp,threshold,'アイテムあり' in row['context'])
    if kind=='boundary':
        actual=int(re.search(r'ちょうど(\d+)',row['context']).group(1))
        threshold=int(re.search(r'(\d+)点',row['question']).group(1))
        return ('boundary',actual,threshold)
    if kind=='comparison':
        nums=tuple(map(int,re.findall(r'(\d+)個',row['context'])))
        return ('comparison',)+nums
    return None


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    data={s:load(a.root/'data/m3_3_v2'/f'{s}.jsonl') for s in ('train','dev','eval_v2')}
    data['smoke_cases']=load(a.root/'examples/smoke_cases.jsonl');data['transfer_probe']=load(a.root/'data/m3_1/transfer_probe.jsonl')
    out={'source_root':str(a.root),'scope':'Archived predictions and code/data only. No GLiClass inference or retraining.'}
    out['metrics']={}
    for model in ('B0','W_fix','W_v2'):
        out['metrics'][model]={}
        for ds in ('eval_v2','smoke_cases','transfer_probe'):
            pred=load(a.root/'runs/m3_3_v2/comparisons'/f'{model}_{ds}_predictions.jsonl')
            out['metrics'][model][ds]=metrics(data[ds],pred)
    out['predictions_checked']=sum(d['count'] for m in out['metrics'].values() for d in m.values())
    out['exact_overlap_order_independent']={}
    for x,y in [('train','dev'),('train','eval_v2'),('dev','eval_v2')]:
        sx={fp(r) for r in data[x]}; sy={fp(r) for r in data[y]}
        out['exact_overlap_order_independent'][x+'/'+y]=len(sx&sy)
    out['semantic_overlap_explicit_rule']={};examples=[]
    for x,y in [('train','dev'),('train','eval_v2'),('dev','eval_v2')]:
        sx=defaultdict(list);sy=defaultdict(list)
        for r in data[x]:
            key=semantic_key(r)
            if key:sx[key].append(r)
        for r in data[y]:
            key=semantic_key(r)
            if key:sy[key].append(r)
        keys=set(sx)&set(sy)
        out['semantic_overlap_explicit_rule'][x+'/'+y]={'shared_states':len(keys),'by_kind':dict(Counter(k[0] for k in keys)),'right_groups':len({r['group_id'] for k in keys for r in sy[k]})}
        for key in sorted(keys):
            examples.append({'splits':[x,y],'semantic_state':key,'left':sx[key],'right':sy[key]})
    out['train_pair_distribution']={}
    for split in ('train','dev','eval_v2'):
        gs=defaultdict(list)
        for r in data[split]:gs[r['group_id']].append(r)
        counter=Counter()
        for rs in gs.values():
            assert len(rs)==2
            counter['same' if rs[0]['target']==rs[1]['target'] else 'different']+=1
        out['train_pair_distribution'][split]=dict(counter)
    for m,ds in out['metrics'].items():
        print(m,{k:(v['correct'],v['count'],round(v['nll'],4),round(v['brier'],4)) for k,v in ds.items()})
    print('pairs',out['metrics']['W_v2']['eval_v2']['pairs'])
    print('semantic_overlap',out['semantic_overlap_explicit_rule'])
    (a.out/'recomputed_summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    (a.out/'semantic_state_examples.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in examples),encoding='utf-8')

if __name__=='__main__':main()
