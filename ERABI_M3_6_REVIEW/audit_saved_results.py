"""Review the supplied ZIP's saved logits, not model execution. CPU, no downloads."""
from __future__ import annotations
import argparse, hashlib, json, math, re, unicodedata
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp

def jl(p): return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
def norm(x): return unicodedata.normalize('NFC',x).strip()
def fingerprint(r):
    return (norm(r['context']),norm(r['question']),tuple(sorted(norm(c['text']) for c in r['choices'])))
def state(r):
    c,q=r['context'],r['question']
    if r['task_family']=='goal_following':
        vals=re.findall(r'(プラン[A-C]|サーバー[A-C]|PC[A-C]|ホテル[A-C]|オフィス[A-C]|便[A-C])は(\d+)([^\d、]+?)で(\d+)([^\d、。]+)',c)
        if len(vals)==3:
            return ('gf',tuple(sorted((int(v1),u1,int(v2),u2.rstrip('です')) for _,v1,u1,v2,u2 in vals)))
    if 'HPは' in c and re.search(r'HPが(\d+)未満',q):
        return ('logic',int(re.search(r'HPが(\d+)未満',q)[1]),int(re.search(r'HPは(\d+)',c)[1]),'アイテムあり' in c)
    if 'ちょうど' in c and re.search(r'(\d+)点',q):
        return ('boundary',int(re.search(r'(\d+)点',q)[1]),int(re.search(r'ちょうど(\d+)点',c)[1]))
    if '在庫数は' in c and re.search(r'受注数は(\d+)個',c):
        return ('inventory',int(re.search(r'在庫数は(\d+)個',c)[1]),int(re.search(r'受注数は(\d+)個',c)[1]))
    return None

def truth(r):
    """Independent checks against the actually rendered text; only known synthetic grammar."""
    c,q=r['context'],r['question']
    bytext={o['text']:o['id'] for o in r['choices']}
    if r['task_family']=='goal_following':
        vals=re.findall(r'(プラン[A-C]|サーバー[A-C]|PC[A-C]|ホテル[A-C]|オフィス[A-C]|便[A-C])は(\d+)([^\d、]+?)で(\d+)([^\d、。]+)',c)
        assert len(vals)==3,(r['id'],c)
        required=q.split('考慮せず、')[-1].split('は問わず、')[-1]
        if '大容量' in required: k,fn=1,max
        elif any(w in required for w in ['安い','低価格','リーズナブル','低コスト','安価']): k,fn=1,min
        elif any(w in required for w in ['早く届く','低遅延','軽量','駅から近い','駅チカ','所要時間が短い']): k,fn=3,min
        else: raise ValueError((r['id'],q))
        ans=fn(vals,key=lambda a:int(a[k]))[0]
        return bytext[ans]
    st=state(r)
    if st and st[0]=='logic':
        _,th,hp,item=st
        if 'かつ' in q: flag=(hp<th and item)
        elif 'または' in q or 'あるいは' in q: flag=(hp<th or item)
        else: raise ValueError((r['id'],q))
        return bytext['回復する' if flag else '待機する']
    if st and st[0]=='boundary':
        _,th,x=st
        if f'{th}点以下' in q: flag=x<=th
        elif f'{th}点未満' in q: flag=x<th
        else: raise ValueError((r['id'],q))
        return bytext['合格' if flag else '不合格']
    if st and st[0]=='inventory':
        _,x,y=st
        if '達して' in q or '以上' in q: flag=x>=y
        elif '多い' in q or '上回' in q: flag=x>y
        else: raise ValueError((r['id'],q))
        return bytext['出荷する' if flag else '出荷を見送る']
    raise ValueError((r['id'],r['task_family'],q))

def calc(records,data,t):
    byid={r['id']:r for r in data}; assert len(byid)==len(data)
    assert len({r['id'] for r in records})==len(records)==len(data)
    assert set(byid)=={r['id'] for r in records}
    out=[]
    for p in records:
        d=byid[p['id']]; ids=[c['id'] for c in p['choices']]
        assert ids==[c['id'] for c in d['choices']]
        assert p['target']==d['target']['choice_id']
        ix=ids.index(d['target']['choice_id'])
        assert p.get('target_index',ix)==ix
        z=np.asarray(p['raw_logits'],dtype=np.float64); assert len(z)==len(ids) and np.isfinite(z).all()
        lp=z/t-logsumexp(z/t); probs=np.exp(lp)
        best=int(np.argmax(z)); correct=ids[best]==d['target']['choice_id']
        assert correct==p['is_correct'] and ids[best]==p['best_candidate_id']
        oh=np.eye(len(ids))[ix]
        out.append(dict(id=p['id'],group=d['group_id'],family=d['task_family'],kind=d.get('rule_kind'),template=d.get('template_family'),k=len(ids),target=d['target']['choice_id'],prediction=ids[best],correct=correct,pmax=float(probs.max()),ptarget=float(probs[ix]),nll=float(-lp[ix]),brier=float(((probs-oh)**2).sum()),probs=probs.tolist()))
    gr=defaultdict(list)
    for r in out:gr[r['group']].append(r)
    pair=None
    if all(len(v)==2 for v in gr.values()):
        pair={'total':len(gr),'both':sum(all(r['correct'] for r in v) for v in gr.values())}
        for mode,check in [('diff',lambda v:v[0]['target']!=v[1]['target']),('same',lambda v:v[0]['target']==v[1]['target'])]:
            sub=[v for v in gr.values() if check(v)]
            pair[mode]={'count':len(sub),'both':sum(all(r['correct'] for r in v) for v in sub)}
    bins=[]
    for lo,hi in [(0,.5),(.5,.7),(.7,.9),(.9,1.0000001)]:
        sub=[r for r in out if lo<=r['pmax']<hi]
        bins.append(dict(low=lo,high=min(hi,1.),count=len(sub),correct=sum(r['correct'] for r in sub),mean_confidence=float(np.mean([r['pmax'] for r in sub])) if sub else None))
    pol={}
    for th in [.8,.9,.95]:
        sub=[r for r in out if r['pmax']>=th]; errs=sum(not r['correct'] for r in sub)
        pol[str(th)]=dict(count=len(sub),errors=errs,coverage=len(sub)/len(out),risk=errs/len(sub) if sub else None)
    bysub={}
    for r in out:
        key=r['family']+':'+str(r['kind']); bysub.setdefault(key,[]).append(r)
    return dict(n=len(out),correct=sum(r['correct'] for r in out),nll=float(np.mean([r['nll'] for r in out])),brier=float(np.mean([r['brier'] for r in out])),pairs=pair,bins=bins,policy=pol,bytask={k:{'n':len(v),'correct':sum(r['correct'] for r in v),'nll':float(np.mean([r['nll'] for r in v])),'brier':float(np.mean([r['brier'] for r in v]))} for k,v in bysub.items()},errors=sorted([r for r in out if not r['correct']],key=lambda r:-r['pmax']))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('bundle_root',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    root=args.bundle_root;args.output.mkdir(parents=True,exist_ok=True)
    paths={'train':'data/m3_3_v2/train.jsonl','dev':'data/m3_3_v2/dev.jsonl','eval_v2':'data/m3_3_v2/eval_v2.jsonl','smoke_cases':'examples/smoke_cases.jsonl','transfer_probe':'data/m3_1/transfer_probe.jsonl','calibration':'data/m3_6_cal/calibration.jsonl','fresh_eval':'data/m3_6_cal/fresh_eval.jsonl'}
    data={k:jl(root/p) for k,p in paths.items()}
    records={k:jl(root/f'runs/m3_6_calibration/raw_logits_{k}.jsonl') for k in ['calibration','fresh_eval']}
    records.update({k:jl(root/f'runs/m3_5_ce10/comparisons/W_v2_ce10_{k}_predictions.jsonl') for k in ['eval_v2','smoke_cases','transfer_probe']})
    opt=minimize_scalar(lambda t:calc(records['calibration'],data['calibration'],t)['nll'],bounds=(.05,20),method='bounded',options={'xatol':1e-8,'maxiter':100})
    artifact=json.loads((root/'runs/m3_6_calibration/calibration.json').read_text());T=artifact['optimization']['optimal_T']
    result={'independent_temperature':float(opt.x),'temperature_nll':float(opt.fun),'artifact_full_temperature':T,'artifact_served_temperature':artifact['temperature'],'sets':{}}
    for k,recs in records.items():
        result['sets'][k]={'T1':calc(recs,data[k],1),'Tcal':calc(recs,data[k],T),'Tserved':calc(recs,data[k],artifact['temperature'])}
        if k!='calibration':
            stored=json.loads((root/f'runs/m3_6_calibration/eval_comparison_{k}.json').read_text())
            assert stored['correct_count']==result['sets'][k]['T1']['correct']
            for mode,storedmode in [('T1','metrics_uncalibrated_T1'),('Tcal','metrics_calibrated_T')]:
                for m in ['nll','brier']:
                    assert abs(result['sets'][k][mode][m]-stored[storedmode]['mean_'+m])<1e-10,(k,m)
    fps={k:set(fingerprint(r) for r in rows) for k,rows in data.items()}
    sts={k:{state(r) for r in rows if state(r)} for k,rows in data.items()}
    new=['calibration','fresh_eval']; old=['train','dev','eval_v2','smoke_cases','transfer_probe']
    result['duplicates']={'within_inputs':{k:len(data[k])-len(fps[k]) for k in new},'input_pairs':{},'semantic_pairs':{},'semantic_parse_rows':{k:sum(state(r) is not None for r in rows) for k,rows in data.items()}}
    for a,b in [('calibration','fresh_eval')]+[(k,j) for k in new for j in old]:
        result['duplicates']['input_pairs'][a+':'+b]=len(fps[a]&fps[b]);result['duplicates']['semantic_pairs'][a+':'+b]=len(sts[a]&sts[b])
    result['label_check']={k:{'checked':len(data[k]),'mismatches':[r['id'] for r in data[k] if truth(r)!=r['target']['choice_id']]} for k in new}
    result['file_hashes']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths.values()}
    result['counts']={k:{'rows':len(v),'groups':len({r['group_id'] for r in v}),'choices':dict(Counter(len(r['choices']) for r in v)),'templates':dict(Counter(r.get('template_family') for r in v)),'kinds':dict(Counter(r.get('rule_kind') for r in v))} for k,v in data.items()}
    (args.output/'recomputed.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    for k in result['sets']:
        a,b=result['sets'][k]['T1'],result['sets'][k]['Tcal']
        print(k,a['correct'],'/',a['n'],'NLL',a['nll'],'->',b['nll'],'Brier',a['brier'],'->',b['brier'])
    print('T',opt.x,'stored',T,'labels',result['label_check'],'duplicates',result['duplicates'])
if __name__=='__main__':main()
