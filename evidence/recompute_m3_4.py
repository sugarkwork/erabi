"""Recompute ERABI saved predictions without loading models or external packages."""
from __future__ import annotations
import argparse,collections,hashlib,json,math,re
from pathlib import Path

def load(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8-sig').splitlines() if x.strip()]

def calc(records,preds):
    nll=[];brier=[];correct=[];unif=[];probs={}
    assert len({p['id'] for p in preds})==len(preds)
    d={p['id']:p for p in preds}
    assert set(d)=={r['id'] for r in records}
    mismatch=[]
    for r in records:
        p=d[r['id']];cid=[x['id'] for x in r['choices']];target=r['target']['choice_id'];y=cid.index(target)
        assert cid==[x['id'] for x in p['choices']]
        z=p['raw_logits'];m=max(z);logsum=m+math.log(sum(math.exp(v-m) for v in z))
        pr=[math.exp(v-logsum) for v in z];best=cid[max(range(len(z)),key=lambda i:z[i])]
        cor=(best==target)
        if (best!=p['best_candidate_id'] or cor!=p['is_correct'] or target!=p['target'] or max(abs(a-b['probability']) for a,b in zip(pr,p['choices']))>1e-5):mismatch.append(r['id'])
        nll.append(logsum-z[y]);brier.append(sum((v-float(i==y))**2 for i,v in enumerate(pr)));correct.append(cor);unif.append(math.log(len(cid)));probs[r['id']]=dict(zip(cid,pr))
    groups=collections.defaultdict(list)
    for r in records:groups[r.get('group_id',r['id'])].append(r)
    pair_summary={};pair_rows=[]
    for g,rs in groups.items():
        if len(rs)!=2:continue
        same=rs[0]['target']['choice_id']==rs[1]['target']['choice_id']
        pp=[d[r['id']]['best_candidate_id'] for r in rs]
        cc=[pp[i]==r['target']['choice_id'] for i,r in enumerate(rs)]
        row={'group_id':g,'target_same':same,'pred_same':pp[0]==pp[1],'n_correct':sum(cc),'family':rs[0]['task_family']+':'+rs[0].get('rule_kind',''),'template_family':rs[0].get('template_family',''),'ids':[r['id'] for r in rs],'targets':[r['target']['choice_id'] for r in rs],'predictions':pp}
        q0=probs[rs[0]['id']];q1=probs[rs[1]['id']]
        if set(q0)==set(q1):row['total_variation']=sum(abs(q0[c]-q1[c]) for c in q0)/2
        pair_rows.append(row)
    for name,fil in [('different',lambda r:not r['target_same']),('same',lambda r:r['target_same'])]:
        rr=[r for r in pair_rows if fil(r)];pair_summary[name]={'pairs':len(rr),'both_correct':sum(r['n_correct']==2 for r in rr),'one_correct':sum(r['n_correct']==1 for r in rr),'zero_correct':sum(r['n_correct']==0 for r in rr),'pred_same':sum(r['pred_same'] for r in rr)}
    metrics={'n':len(records),'correct':sum(correct),'accuracy':sum(correct)/len(records),'mean_nll':sum(nll)/len(nll),'mean_brier':sum(brier)/len(brier),'uniform_nll':sum(unif)/len(unif),'pairs':pair_summary,'mismatches':mismatch}
    bins=[]
    for lo,hi in [(0,.5),(.5,.7),(.7,.9),(.9,1.000001)]:
        idx=[i for i,r in enumerate(records) if lo<=max(probs[r['id']].values())<hi]
        bins.append({'lo':lo,'hi':hi,'n':len(idx),'correct':sum(correct[i] for i in idx),'mean_pmax':sum(max(probs[records[i]['id']].values()) for i in idx)/len(idx) if idx else None})
    metrics['pmax_bins']=bins
    return metrics,pair_rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--current',type=Path,required=True);ap.add_argument('--previous',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(exist_ok=True,parents=True)
    ds={'eval_v2':'data/m3_3_v2/eval_v2.jsonl','smoke_cases':'examples/smoke_cases.jsonl','transfer_probe':'data/m3_1/transfer_probe.jsonl'}
    out={'scope':'Recomputed from uploaded saved logits, not real-model inference; old individual predictions taken from previously uploaded followup ZIP.','datasets':{},'unchanged_data':{}}
    for k,rel in ds.items():
        rr=load(a.current/rel);out['datasets'][k]={}
        for model in ['B0','W_fix','W_v2','W_v2_gradfix']:
            src=(a.current/'runs/m3_4_gradfix/comparisons' if model.endswith('gradfix') else a.previous/'runs/m3_3_v2/comparisons')/f'{model}_{k}_predictions.jsonl'
            pp=load(src);met,pairs=calc(rr,pp);out['datasets'][k][model]=met
            if k=='eval_v2':
                (a.out/f'{model}_pair_details.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in pairs),encoding='utf-8')
                byid={p['id']:p for p in pp};subsets={}
                for fam in ['goal_following','explicit_rule']:
                    subs=[r for r in rr if r['task_family']==fam]
                    if subs:subsets[fam]={'n':len(subs),'correct':sum(byid[r['id']]['best_candidate_id']==r['target']['choice_id'] for r in subs)}
                for case in ['c1','c2']:
                    subs=[r for r in rr if r['task_family']=='goal_following' and r['id'].endswith(case)]
                    subsets['goal_'+case]={'n':len(subs),'correct':sum(byid[r['id']]['best_candidate_id']==r['target']['choice_id'] for r in subs)}
                met['subsets']=subsets
    for s in ['train','dev','eval_v2']:
        p=Path('data/m3_3_v2')/(s+'.jsonl');b=(a.current/p).read_bytes();out['unchanged_data'][s]={'sha256':hashlib.sha256(b).hexdigest(),'identical_to_previous':b==(a.previous/p).read_bytes()}
    (a.out/'recomputed_metrics.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    for dsname,models in out['datasets'].items():
        print(dsname)
        for m,stats in models.items():
            print(m,stats['correct'],stats['n'],round(stats['mean_nll'],4),round(stats['mean_brier'],4),stats['pairs'],'mismatches',len(stats['mismatches']))
            if 'subsets' in stats: print(' ',stats['subsets'])
    new_pairs=load(a.out/'W_v2_gradfix_pair_details.jsonl')
    notsw=[p for p in new_pairs if not p['target_same'] and p['pred_same']]
    print('UNSWITCHED TV min/max/mean',min(p['total_variation'] for p in notsw),max(p['total_variation'] for p in notsw),sum(p['total_variation'] for p in notsw)/len(notsw))
    print('FAIL IDS',[(p['group_id'],p['family'],p['predictions']) for p in notsw[:10]])

if __name__=='__main__':main()
