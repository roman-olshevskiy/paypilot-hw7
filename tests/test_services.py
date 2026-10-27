import unittest,os,json,urllib.request,base64
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
@unittest.skipUnless(os.environ.get('HW7_SERVICES')=='1','Explicit external service test disabled')
class Services(unittest.TestCase):
 def test_openrouter_models_and_usage(self):
  values={}
  for line in (ROOT.parent/'paypilot-stand-shared/.env').read_text(encoding='utf-8-sig').splitlines():
   if '=' in line and not line.lstrip().startswith('#'):
    k,v=line.split('=',1);values[k.strip()]=v.strip().strip(chr(34)).strip(chr(39))
  req=urllib.request.Request('https://openrouter.ai/api/v1/key',headers={'Authorization':'Bearer '+values['OPENROUTER_API_KEY']})
  with urllib.request.urlopen(req,timeout=30) as res:data=json.load(res)['data']
  phase=os.environ.get('HW7_BILLING_PHASE','before')
  out=ROOT/'evidence'/('key-usage-'+phase+'.json');self.assertFalse(out.exists());out.write_text(json.dumps({k:data.get(k) for k in ['usage','byok_usage']},indent=2))
  if phase=='before':
   with urllib.request.urlopen('https://openrouter.ai/api/v1/models',timeout=30) as res:models=json.load(res)['data']
   wanted=['anthropic/claude-haiku-5.5','google/gemini-2.5-flash'];selected=[{k:m.get(k) for k in ['id','pricing','context_length']} for m in models if m['id'] in wanted]
   self.assertEqual(len(selected),2);(ROOT/'evidence/model-prices-api.json').write_text(json.dumps(selected,indent=2))
