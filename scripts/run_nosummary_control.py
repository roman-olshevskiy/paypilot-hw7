"""Control B3 with summarization disabled; queued after Docker confirmation."""
import sys,time,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from hw7_capture import guard,loadkit,Capture,read,write

def main():
 guard();deadline=time.time()+3600
 while not (ROOT/'evidence/docker-clean-clone.json').exists():
  if time.time()>deadline:raise RuntimeError('Docker confirmation incomplete')
  time.sleep(3)
 if (ROOT/'evidence/no-summary-control-index.json').exists():raise RuntimeError('Control already exists')
 m=loadkit();sc=read(ROOT/'l08/kit/scenarios/b3-summary-loses-case.json');sc['id']='B3-NO-SUMMARY';sc['title']='B3 control with summary disabled'
 for settings in sc['conditions'].values():settings['summarize_after']=20
 sc['assertions']=[{'kind':'summary_absent'}]
 original_check=m.check
 def check(assertion,rows):
  if assertion['kind']=='summary_absent':return all(x['summary'] is None for x in rows),'all four steps contain no agent.summarize'
  return original_check(assertion,rows)
 m.check=check;cap=Capture('no-summary-control',m);original=m.run
 def run(scenario,condition,settings,runs,prices,show_table,prompt_step=None):
  cap.context={'scenario':scenario['id'],'condition':condition,'settings':settings};cap.repeat=0
  return original(scenario,condition,settings,runs,prices,show_table,prompt_step)
 m.run=run
 with tempfile.TemporaryDirectory(prefix='hw7-nosummary-') as tmp:
  p=Path(tmp);(p/'scenarios').mkdir();write(p/'scenarios/control.json',sc);(p/'prices.json').write_bytes((ROOT/'l08/kit/prices.json').read_bytes());m.ROOT=p
  def execute():
   old=sys.argv[:];sys.argv=['run_dialog.py','--scenario','B3-NO-SUMMARY','--runs','5','--json',str(cap.folder/'native-results.json')]
   try:m.main()
   finally:sys.argv=old
  cap.execute('no-summary-control',execute)
 write(ROOT/'evidence/no-summary-control-index.json',{'folder':cap.folder.relative_to(ROOT).as_posix()})
 print('NO-SUMMARY CONTROL COMPLETE',flush=True)
if __name__=='__main__':main()
