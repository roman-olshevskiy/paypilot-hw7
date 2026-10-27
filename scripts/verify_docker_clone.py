"""Paid canonical-equivalent L03 CLI in clean Docker clone, both profiles, complete captures."""
import os,sys,json,subprocess,tempfile,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from hw7_capture import guard,read,write

def main():
 guard();proof_path=ROOT/'evidence/docker-clean-clone.json'
 if proof_path.exists():raise RuntimeError('Already executed; no automatic repeat')
 sha=hashlib.sha256((ROOT/'l08/forecast-before-runs.md').read_bytes()).hexdigest()
 results=[]
 with tempfile.TemporaryDirectory(prefix='hw7-docker-clone-') as tmp:
  clone=Path(tmp)/'repo';subprocess.run(['git','clone','--quiet','--no-hardlinks',str(ROOT),str(clone)],check=True)
  assert not subprocess.check_output(['git','status','--porcelain'],cwd=clone)
  assert (clone/'sets/l05_dialogs.jsonl').read_bytes()==(ROOT/'sets/l05_dialogs.jsonl').read_bytes()
  env=os.environ.copy();env['STAND_DIR']=(ROOT.parent/'paypilot-stand-shared').as_posix();env['COMPOSE_PROJECT_NAME']='hw7-chain-ready';env['EVAL_STAND_URL']='http://host.docker.internal:8000'
  settings=json.dumps({'model':'anthropic/claude-haiku-5.5','summarize_after':20,'clock':'2026-09-15T10:00:00Z'})
  for profile in ['lesson-08','clean']:
   args=['docker','compose','run','--rm','-e','HW7_PAID=1','-e','HW7_FORECAST_SHA='+sha,'--entrypoint','python','eval','scripts/docker_capture_entry.py','--set','l05_dialogs','--gate','all','--profile',profile,'--settings',settings]
   print('Start real Docker clone '+profile,flush=True)
   before=set((clone/'reports').glob('*.json'))
   proc=subprocess.run(args,cwd=clone,env=env,check=True)
   index=read(clone/('evidence/docker-budget-'+profile+'-index.json'));source=clone/index['folder'];target=ROOT/index['folder']
   assert not target.exists();shutil.copytree(source,target)
   write(ROOT/('evidence/docker-budget-'+profile+'-index.json'),index)
   for report in set((clone/'reports').glob('*.json'))-before:shutil.copy2(report,ROOT/'reports'/report.name)
   raw=read(source/'native-results.json');results.append({'profile':profile,'actual_command':args,'native_cli_args':args[args.index('--set'):],'cases':raw['total'],'passed':raw['passed'],'folder':index['folder']})
  assert not subprocess.check_output(['git','diff','--name-only'],cwd=clone)
  proof={'cloned_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=clone,text=True).strip(),'clone_clean_at_start':True,'tracked_source_unchanged':True,'scope':'Real paid Docker native L03 CLI, capture wrapper preserves every step. lesson-08 then clean; not replay. Historical host runs kept separate.','results':results}
  write(proof_path,proof);print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
