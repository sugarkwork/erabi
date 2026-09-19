"""Offline reproductions using uploaded code; no real model or downloads."""
from __future__ import annotations
import argparse, ast, copy, hashlib, importlib.util, json, random, sys, tempfile, types
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 sys.path.insert(0,str(a.root/'src'));sys.path.insert(0,str(a.root))
 from erabi.__main__ import load_and_verify_calibration
 from erabi.api import create_app
 from fastapi.testclient import TestClient
 from erabi.schema import ChoiceResponse,ChoiceOutput,DecisionOutput,CalibrationOutput,UsageOutput
 from erabi.evaluate import compute_softmax
 # The actual API/loader is used unchanged, with a fake scorer instead of GLiClass.
 class Fake:
  model_id='fake-local-model'
  def predict(self,req,temperature=1.,calibration=None):
   probs=compute_softmax([0.,4.],temperature)
   return ChoiceResponse(schema_version='1',model_id=self.model_id,choices=[ChoiceOutput(id=c.id,probability=p) for c,p in zip(req.choices,probs)],best_candidate_id=req.choices[1].id,decision=DecisionOutput(status='review',reason='policy_not_configured'),calibration=calibration or CalibrationOutput(status='none',artifact_id=None),usage=UsageOutput(input_tokens=5,truncated=False))
 out={}
 original=json.loads((a.root/'runs/m3_6_calibration/calibration.json').read_text())
 source=(a.root/'scripts/run_m3_6_calibration.py').read_text()
 assert 'adoption_status = "applied_scoped"' in source
 with tempfile.TemporaryDirectory() as td:
  t=Path(td); gen=copy.deepcopy(original);gen['status']='applied_scoped';pgen=t/'generated.json';pgen.write_text(json.dumps(gen))
  app=create_app(model_id='fake-local-model',calibration_path=str(pgen),engine_factory=Fake)
  with TestClient(app) as client:
   health=client.get('/health').json()
   pred=client.post('/predict',json={'context':'検査','question':'候補を選ぶ','choices':[{'id':'a','text':'A'},{'id':'b','text':'B'}]}).json()
  out['generated_status_consumed']={'generated_status':'applied_scoped','intended_temperature':original['temperature'],'actual_health':health,'actual_prediction':pred}
  try:
   with TestClient(create_app(model_id='fake-local-model',calibration_path=str(pgen),require_calibration=True,engine_factory=Fake)):pass
  except RuntimeError as e:out['required_calibration_rejected']=str(e)
  papplied=t/'applied.json';papplied.write_text(json.dumps(original))
  temp,co,_=load_and_verify_calibration(str(papplied),'not-a-real-directory/or/model')
  out['nonlocal_model_verification_bypass']={'model_id':'not-a-real-directory/or/model','loader_returned_status':co.status,'loader_returned_temperature':temp,'model_hash_checked':False}
  # Import only the exact hash helper, avoiding unavailable inference dependencies.
  tree=ast.parse((a.root/'src/erabi/calibrate.py').read_text())
  node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compute_file_sha256')
  mod=types.ModuleType('erabi.calibrate');mod.__dict__['hashlib']=hashlib
  exec(compile(ast.Module(body=[node],type_ignores=[]),'uploaded_calibrate_hash_helper','exec'),mod.__dict__)
  sys.modules['erabi.calibrate']=mod
  ck=t/'checkpoint';ck.mkdir()
  files={}
  for name in ['model.safetensors','config.json','tokenizer.json','tokenizer_config.json']:
   (ck/name).write_bytes(b'fake '+name.encode());files[name]=hashlib.sha256((ck/name).read_bytes()).hexdigest()
  wrong=copy.deepcopy(original);wrong['target_model']['files']=files
  wrong['contract'].update({'max_tokens':1,'schema_version':'999','precision':'not-the-runtime-precision','formatter_version':'not-the-runtime-format'})
  cp=t/'wrong_contract.json';cp.write_text(json.dumps(wrong))
  temp,co,_=load_and_verify_calibration(str(cp),str(ck))
  out['contract_mismatch_accepted']={'loader_status':co.status,'temperature':temp,'contract':wrong['contract'],'note':'Real loader and real hash helper; fake local checkpoint bytes, no model instantiation.'}
  # Round-trip a synthetic goal-following group through the actual state extractor.
  spec=importlib.util.spec_from_file_location('builder',a.root/'scripts/build_m3_6_data.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
  pair,state=b.generate_goal_following_scenario('probe',0,random.Random(42))
  dpath=t/'group.jsonl';dpath.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in pair),encoding='utf-8')
  extracted=b.extract_existing_semantic_states(dpath)
  out['goal_state_roundtrip']={'generated_state':state,'extracted_states':list(extracted),'matches_own_state':state in extracted}
 # Read-only code evidence for cached-logit metadata and status discrepancy.
 out['current_artifact_vs_summary_status']={'artifact':original['status'],'summary':json.loads((a.root/'runs/m3_6_calibration/summary_report.json').read_text())['adoption']['status']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
