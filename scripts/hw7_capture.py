"""Real native eval with durable per-chat capture, forecast guard and restore."""
import sys,os,json,time,uuid,hashlib,subprocess,importlib.util,contextlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp')
 data=(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
 for n in range(8):
  try:tmp.write_bytes(data);tmp.replace(p);return
  except PermissionError:
   if n==7:raise
   time.sleep(.1*(n+1))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard():
 if os.environ.get('HW7_PAID')!='1':raise RuntimeError('Set HW7_PAID=1 for explicitly paid runs')
 proof=read(ROOT/'evidence/forecast-commit.json');commit=proof['commit']
 saved=subprocess.check_output(['git','show',commit+':l08/forecast-before-runs.md'],cwd=ROOT)
 assert saved==(ROOT/'l08/forecast-before-runs.md').read_bytes()
def loadkit():
 spec=importlib.util.spec_from_file_location('l08_native',ROOT/'l08/kit/run_dialog.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class Capture:
 def __init__(self,label,module):
  self.module=module;self.original=module._call;self.rows=[];self.attempts=[];self.context={};self.repeat=0;self.step=0
  self.folder=ROOT/'evidence/runs'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'-'+label+'-'+uuid.uuid4().hex[:6]);self.folder.mkdir(parents=True)
 def call(self,method,path,*args,**kw):
  if method=='POST' and path=='/api/_test/reset':self.repeat+=1;self.step=0
  if not(method=='POST' and path=='/chat'):return self.original(method,path,*args,**kw)
  self.step+=1;body=args[0] if args else kw.get('body',kw.get('payload'));record={**self.context,'repeat':self.repeat,'step':self.step,'request':body,'status':'started'}
  self.attempts.append(record);write(self.folder/'attempts.json',self.attempts);t=time.perf_counter()
  try:res=self.original(method,path,*args,**kw)
  except Exception as e:
   record.update(status='failed_or_unknown',error=str(e));write(self.folder/'attempts.json',self.attempts);raise
  record.update(status='response_received',request_id=res.get('request_id'))
  row={**self.context,'repeat':self.repeat,'step':self.step,'request':body,'response':res,'wall_ms':(time.perf_counter()-t)*1000,'status':'response_saved'}
  self.rows.append(row);write(self.folder/'captures.json',self.rows);write(self.folder/'attempts.json',self.attempts)
  row['trace']=self.original('GET','/api/_test/traces/'+res['request_id']);row['state_disputes']=self.original('GET','/api/_test/state/disputes');row['status']='complete';write(self.folder/'captures.json',self.rows)
  return res
 def snapshot(self):return self.original('GET','/api/_test/defects')
 def execute(self,label,fn):
  before=self.snapshot();error=None;self.module._call=self.call;t=time.time()
  try:result=fn()
  except BaseException as e:error=repr(e);raise
  finally:
   self.module._call=self.original
   self.original('PUT','/api/_test/profile',{'profile':before['profile']})
   self.original('PUT','/api/_test/defects',{'defects':','.join(before['extra_defects'])})
   restored=self.snapshot()
   files={p.name:sha(p) for p in self.folder.glob('*.json')}
   write(self.folder/'manifest.json',{'label':label,'error':error,'responses':len(self.rows),'complete':sum(x['status']=='complete' for x in self.rows),'attempts':len(self.attempts),'duration_seconds':time.time()-t,'before':before,'restored':restored,'sha256':files,'scope':'Seed DB reset is real; arbitrary pre-run DB/session state not restored; per-request overrides leave global model/clock unchanged'})
   print('CAPTURE',self.folder,flush=True)
  return result

def run_l08(label,args):
 guard();m=loadkit();cap=Capture(label,m)
 original=m.run
 def run(sc,condition,settings,runs,prices,show_table,prompt_step=None):
  cap.context={'scenario':sc['id'],'condition':condition,'settings':settings};cap.repeat=0
  return original(sc,condition,settings,runs,prices,show_table,prompt_step)
 m.run=run
 def execute():
  saved=sys.argv[:];sys.argv=['run_dialog.py',*args,'--json',str(cap.folder/'native-results.json')]
  try:m.main()
  finally:sys.argv=saved
 cap.execute(label,execute);return cap.folder

def run_l03(label,args,calibration=False):
 guard();import stand,runner,cli
 cap=Capture(label,stand);original=runner.run_case
 def case(c):
  cap.context={'scenario':c['id'],'condition':label,'settings':{}};cap.repeat=0
  old=os.environ.get('STAND_SETTINGS')
  settings={'clock':c.get('context',{}).get('clock','2026-09-15T10:00:00Z'),'summarize_after':c['additional_metadata'].get('summarize_after',20),'model':'anthropic/claude-haiku-5.5'}
  os.environ['STAND_SETTINGS']=json.dumps(settings);cap.context['settings']=settings
  if calibration:c=json.loads(json.dumps(c));c['additional_metadata']['budget']={'tokens_total':100000000,'latency_ms':10000000}
  try:return original(c)
  finally:
   if old is None:os.environ.pop('STAND_SETTINGS',None)
   else:os.environ['STAND_SETTINGS']=old
 runner.run_case=case
 try:
  def execute():
   code=cli.main(args)
   if code not in (0,1):raise RuntimeError('L03 transport/runner error '+str(code))
   return code
  cap.execute(label,execute)
 finally:runner.run_case=original
 return cap.folder
if __name__=='__main__':
 mode,label=sys.argv[1:3];args=sys.argv[3:]
 folder=run_l08(label,args) if mode=='l08' else run_l03(label,args,mode=='calibration')
 write(ROOT/'evidence'/(label+'-index.json'),{'folder':folder.relative_to(ROOT).as_posix()})
