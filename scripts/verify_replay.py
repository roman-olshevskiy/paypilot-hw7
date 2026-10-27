"""Clean Git clone: native L03 CLI on recorded fixtures, no real HTTP/model calls."""
import sys,subprocess,tempfile,json,time,types,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def worker(profile,out):
 sys.path.insert(0,str(ROOT));import cli,runner,stand
 index=json.loads((ROOT/('evidence/docker-budget-'+profile+'-index.json')).read_text());folder=ROOT/index['folder']
 captures=json.loads((folder/'captures.json').read_text());expected=json.loads((folder/'native-results.json').read_text())
 bycase={};traces={x['response']['request_id']:x['trace'] for x in captures}
 for row in captures:bycase.setdefault(row['scenario'],{}).setdefault(row['repeat'],[]).append(row)
 state={'case':None,'repeat':0,'step':0,'clock':0,'profile':profile,'real_http_calls':0,'fixture_chat_calls':0}
 original=runner.run_case
 def run_case(case):
  state.update(case=case['id'],repeat=0,step=0,clock=0)
  try:return original(case)
  finally:state['case']=None
 def call(method,path,payload=None,**kw):
  if path=='/health':return {'status':'ok','provider':'recorded-replay'}
  if path=='/api/_test/defects':return {'profile':state['profile'],'extra_defects':[]}
  if path=='/api/_test/profile':state['profile']=payload['profile'];return {}
  if path=='/api/_test/prompt':return {'version':expected['prompt_version']}
  if path=='/api/_test/reset':state['repeat']+=1;state['step']=0;return {}
  if path=='/chat':
   row=bycase[state['case']][state['repeat']][state['step']];state['step']+=1;state['fixture_chat_calls']+=1
   assert row['request']['message']==payload['message']
   return row['response']
  if path.startswith('/api/_test/traces/'):return traces[path.rsplit('/',1)[1]]
  raise RuntimeError('Network forbidden; unexpected native call '+method+' '+path)
 def clock():
  if state['case'] is None:return time.time()
  row=next(x for x in expected['cases'] if x['id']==state['case']);n=state['clock'];state['clock']+=1
  return 100000+(row['budget_samples'][n//2]['latency_ms']/1000 if n%2 else 0)
 stand._call=call;runner.run_case=run_case;runner.time=types.SimpleNamespace(time=clock)
 runner.REPORTS_DIR=Path(out);runner.REPORTS_DIR.mkdir(exist_ok=True,parents=True)
 code=cli.main(['--set','l05_dialogs','--profile',profile,'--gate','all'])
 report=json.loads(next(Path(out).glob('*.json')).read_text())
 assert [(x['id'],x['verdict']['passed']) for x in report['cases']]==[(x['id'],x['verdict']['passed']) for x in expected['cases']]
 print(json.dumps({'profile':profile,'native_cli_exit':code,'verdicts_reproduced':len(report['cases']),'fixture_chat_calls':state['fixture_chat_calls'],'real_http_calls':0,'real_model_calls':0}))
def main():
 if len(sys.argv)>1 and sys.argv[1]=='--worker':worker(sys.argv[2],sys.argv[3]);return
 with tempfile.TemporaryDirectory(prefix='hw7-replay-') as tmp:
  clone=Path(tmp)/'repo';subprocess.run(['git','clone','--quiet','--no-hardlinks',str(ROOT),str(clone)],check=True)
  assert not subprocess.check_output(['git','status','--porcelain'],cwd=clone)
  outputs=[]
  for profile in ['clean','lesson-08']:
   result=subprocess.run([sys.executable,str(clone/'scripts/verify_replay.py'),'--worker',profile,str(Path(tmp)/profile)],cwd=clone,text=True,encoding='utf-8',capture_output=True,check=True)
   outputs.append(json.loads(result.stdout.splitlines()[-1]))
  assert not subprocess.check_output(['git','status','--porcelain'],cwd=clone)
  proof={'cloned_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=clone,text=True).strip(),'clean_before_and_after':True,'scope':'Actual native Python CLI in a clean clone with recorded HTTP fixtures and recorded per-dialog latency; not a new live or Docker run','results':outputs}
  (ROOT/'evidence/clean-clone-replay.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
