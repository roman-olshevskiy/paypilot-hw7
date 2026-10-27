import unittest,json,hashlib,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def rd(p):return json.loads((R/p).read_text(encoding='utf-8'))
class FinalEvidence(unittest.TestCase):
 def test_capture_integrity_and_restore(self):
  ids=[]
  for p in (R/'evidence').glob('*-index.json'):
   i=json.loads(p.read_text(encoding='utf-8'))
   if 'folder' not in i:continue
   folder=R/i['folder'];m=json.loads((folder/'manifest.json').read_text(encoding='utf-8'));rows=json.loads((folder/'captures.json').read_text(encoding='utf-8'))
   self.assertIsNone(m['error']);self.assertEqual(m['complete'],len(rows));self.assertEqual(m['attempts'],len(rows))
   for k in ['profile','extra_defects']:self.assertEqual(m['before'].get(k),m['restored'].get(k))
   for n,h in m['sha256'].items():self.assertEqual(hashlib.sha256((folder/n).read_bytes()).hexdigest(),h)
   ids += [r['response']['request_id'] for r in rows]
  self.assertEqual(len(ids),946);self.assertEqual(len(set(ids)),946)
 def test_frozen_sources_and_final_results(self):
  self.assertEqual(hashlib.sha256((R/'sets/l05_dialogs.jsonl').read_bytes()).hexdigest(),rd('evidence/budget-freeze.json')['sha256'])
  self.assertEqual(hashlib.sha256((R/'sources/l05_dialogs-hw4.jsonl').read_bytes()).hexdigest(),'d7ea1a1c292f498d48c311229d82d3b35f95a98d11df45f9c2996351e355141e')
  a=rd('evidence/analysis.json');self.assertEqual(a['budget_reports']['clean']['passed'],6);self.assertEqual(a['budget_reports']['lesson-08']['passed'],2)
  b=rd('evidence/billing-reconciliation.json');self.assertLess(abs(b['key_minus_provider_usd']),1e-8)
 def test_authored_links_and_blank_template(self):
  files=[R/'README.md',R/'SUBMISSION.md']+list((R/'l08').glob('*.md'))
  for p in files:
   for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
    if '://' in target or target.startswith('#'):continue
    self.assertTrue((p.parent/target.split('#')[0]).exists(),f'{p.name}: {target}')
  text=(R/'l08/observability-cost-report.template.md').read_text(encoding='utf-8')
  for value in ['PayPilot','TX-0401','CUS-','Haiku','Gemini','0.004']:self.assertNotIn(value,text)
