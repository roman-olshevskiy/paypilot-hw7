"""Sequential remaining HW7 native runs; never overlap global reset/profile."""
import sys,os,time,json,subprocess,math,statistics,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from hw7_capture import read,write,run_l08,run_l03,guard

def main():
 guard();deadline=time.time()+2400
 while not (ROOT/'evidence/full-b4-index.json').exists():
  if time.time()>deadline:raise RuntimeError('B4 not complete; stop before other runs')
  time.sleep(3)
 print('B4 complete; start B3',flush=True)
 folder=run_l08('full-b3',['--scenario','B3','--runs','5'])
 write(ROOT/'evidence/full-b3-index.json',{'folder':folder.relative_to(ROOT).as_posix()})
 print('Start independent clean budget calibration',flush=True)
 folder=run_l03('calibration-clean',['--set','l05_dialogs','--profile','clean','--gate','release'],True)
 write(ROOT/'evidence/calibration-clean-index.json',{'folder':folder.relative_to(ROOT).as_posix()})
 report=read(folder/'native-results.json');cases=[json.loads(x) for x in (ROOT/'sets/l05_dialogs.jsonl').read_text(encoding='utf-8').splitlines()]
 calibration={}
 for row in report['cases']:
  samples=row['budget_samples'];tokens=statistics.median(x['dialog_tokens'] for x in samples);latency=statistics.median(x['latency_ms'] for x in samples)
  margin=0.05 if row['id']=='BUD-D15' else 0.15
  thresholds={'tokens_total':math.ceil(tokens*(1+margin)),'latency_ms':math.ceil(latency*2)}
  next(c for c in cases if c['id']==row['id'])['additional_metadata']['budget']=thresholds
  calibration[row['id']]={'samples':samples,'median_tokens':tokens,'median_latency_ms':latency,'thresholds':thresholds,'token_margin_percent':margin*100,'latency_margin_percent':100}
 data=''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in cases).encode()
 (ROOT/'sets/l05_dialogs.jsonl').write_bytes(data)
 write(ROOT/'evidence/budget-calibration.json',calibration)
 write(ROOT/'evidence/budget-freeze.json',{'sha256':hashlib.sha256(data).hexdigest(),'method':'Independent clean calibration; tokens median+5% for D15, +15% for other cases; latency median+100%, fixed before final clean and defect','calibration_folder':folder.relative_to(ROOT).as_posix()})
 subprocess.run(['git','add','sets/l05_dialogs.jsonl','evidence/budget-calibration.json','evidence/budget-freeze.json','runner.py','loader.py','scripts/hw7_capture.py','scripts/run_remaining.py','tests/test_hw7.py'],cwd=ROOT,check=True)
 subprocess.run(['git','commit','-m','Freeze calibrated budget thresholds before final clean and defect runs'],cwd=ROOT,check=True)
 for profile in ['clean','lesson-08']:
  print('Start final L03 '+profile,flush=True)
  folder=run_l03('budget-'+profile,['--set','l05_dialogs','--profile',profile,'--gate','all'])
  write(ROOT/('evidence/budget-'+profile+'-index.json'),{'folder':folder.relative_to(ROOT).as_posix()})
 print('ALL MAIN SERIES COMPLETE',flush=True)
if __name__=='__main__':main()
