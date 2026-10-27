import unittest,sys,json,os,urllib.request,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import runner
class Budget(unittest.TestCase):
 def result(self,tokens=100,latency=1000,traces=None):return {'dialog_tokens':tokens,'latency_ms':latency,'step_traces':traces or []}
 def tree(self,args):return {'children':[{'name':'tool.get_transactions','attributes':{'tool.arguments':a}} for a in args]}
 def test_arguments_and_early_step(self):
  different=self.tree([{'a':1},{'a':2}]);same=self.tree([{'a':1,'b':2},{'b':2,'a':1}]);meta={'budget':{'identical_tool_calls_max':1}}
  self.assertTrue(runner._budget(meta,[self.result(traces=[different])]).passed)
  verdict=runner._budget(meta,[self.result(traces=[same,{}])]);self.assertFalse(verdict.passed);self.assertEqual(verdict.level,1)
 def test_median_not_sum_and_dialog_latency(self):
  meta={'budget':{'tokens_total':120,'latency_ms':1500}}
  self.assertTrue(runner._budget(meta,[self.result() for _ in range(4)]+[self.result(9000,9000)]).passed)
  self.assertFalse(runner._budget(meta,[self.result(130) for _ in range(5)]).passed)
 def test_six_cases_and_levels(self):
  cases=[json.loads(x) for x in (ROOT/'sets/l05_dialogs.jsonl').read_text(encoding='utf-8').splitlines()];self.assertEqual(len(cases),6)
  import loader;self.assertEqual(len(loader.load(ROOT/'sets/l05_dialogs.jsonl')),6)
  for c in cases:
   m=c['additional_metadata'];daily=set(m['budget'])=={'identical_tool_calls_max'}
   self.assertEqual(m['gate'],'daily' if daily else 'release');self.assertEqual(m['runs'],1 if daily else 5)
 def test_paid_guard(self):
  from hw7_capture import guard
  old=os.environ.pop('HW7_PAID',None)
  try:self.assertRaises(RuntimeError,guard)
  finally:
   if old:os.environ['HW7_PAID']=old
@unittest.skipUnless(os.environ.get('HW7_ENV')=='1','Explicit readiness disabled')
class Readiness(unittest.TestCase):
 def test_runtime(self):
  with urllib.request.urlopen('http://localhost:8000/health',timeout=30) as response:h=json.load(response)
  self.assertEqual(h['provider'],'openrouter');self.assertIn('langfuse',h.get('trace_backends',[]))
  with urllib.request.urlopen('http://localhost:3000/api/public/health',timeout=30) as response:self.assertEqual(response.status,200)
  script="import os,json;print(json.dumps({k:os.environ.get(k,'') for k in ['LLM_PROVIDER','HTTPS_PROXY','SSL_CERT_FILE','TRACE_CAPTURE_CONTENT']}))"
  v=json.loads(subprocess.check_output(['docker','compose','exec','-T','stand','python','-c',script],cwd=ROOT.parent/'paypilot-stand-shared',text=True));self.assertFalse(v['HTTPS_PROXY']);self.assertEqual(v['TRACE_CAPTURE_CONTENT'],'1')
  (ROOT/'evidence/readiness.json').write_text(json.dumps({'health':h,'runtime':v},indent=2))
