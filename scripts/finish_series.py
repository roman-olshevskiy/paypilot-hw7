"""After host validation, apply pre-registered clean amendment and run independent Docker confirmation."""
import sys,time,json,subprocess,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from hw7_capture import read,write,guard

def main():
 guard();deadline=time.time()+2400
 while not (ROOT/'evidence/budget-lesson-08-index.json').exists():
  if time.time()>deadline:raise RuntimeError('Host validation incomplete')
  time.sleep(3)
 print('Host series complete; apply pre-registered H04 clean amendment',flush=True)
 cases_path=ROOT/'sets/l05_dialogs.jsonl';old=cases_path.read_bytes()
 (ROOT/'sources/l05_dialogs-budget-v1.jsonl').write_bytes(old)
 write(ROOT/'evidence/budget-freeze-v1.json',read(ROOT/'evidence/budget-freeze.json'))
 write(ROOT/'evidence/budget-calibration-v1.json',read(ROOT/'evidence/budget-calibration.json'))
 intent=read(ROOT/'evidence/calibration-amendment-intent.json');cal=read(ROOT/'evidence/budget-calibration.json')
 cal['BUD-H04']['initial_median_tokens']=cal['BUD-H04']['median_tokens'];cal['BUD-H04']['median_tokens']=intent['combined_clean_median']
 cal['BUD-H04']['thresholds']['tokens_total']=intent['new_token_threshold'];cal['BUD-H04']['token_samples_v2']=intent['old_clean_calibration_tokens']+intent['additional_clean_validation_tokens']
 cal['BUD-H04']['method_v2']='Tokens median of10 clean dialogues plus15%; latency retains original5-sample median plus100%. Intent registered before first own defect results.'
 cases=[json.loads(x) for x in old.decode().splitlines()]
 next(c for c in cases if c['id']=='BUD-H04')['additional_metadata']['budget']['tokens_total']=intent['new_token_threshold']
 data=''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in cases).encode();cases_path.write_bytes(data)
 write(ROOT/'evidence/budget-calibration.json',cal)
 write(ROOT/'evidence/budget-freeze.json',{'version':2,'sha256':hashlib.sha256(data).hexdigest(),'method':'H04 clean-only expansion pre-registered in calibration-amendment-intent; other budgets unchanged; frozen before independent Docker confirmation','previous_version':'evidence/budget-freeze-v1.json','original_host_series_scope':'V1 host runs are validation diagnostics, not final V2 confirmation'})
 subprocess.run(['git','add','--all'],cwd=ROOT,check=True)
 subprocess.run(['git','commit','-m','Preserve host validation and freeze clean-only H04 revision before Docker confirmation'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_docker_clone.py')],cwd=ROOT,check=True)
 print('DOCKER CONFIRMATION COMPLETE',flush=True)
if __name__=='__main__':main()
