"""Offline analysis; all source captures remain unchanged."""
import json,sys,statistics,math,hashlib
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from hw7_capture import read,write,loadkit
kit=loadkit();prices=kit.load_prices()
def stats(values):return {'median':statistics.median(values),'min':min(values),'max':max(values)}
def rows_for(label):return read(ROOT/read(ROOT/('evidence/'+label+'-index.json'))['folder']/'captures.json')
def main():
 evidence=ROOT/'evidence';allrows=[];batches=[]
 for idx in sorted(evidence.glob('*-index.json')):
  index=read(idx)
  if 'folder' not in index:continue
  folder=ROOT/index['folder'];manifest=read(folder/'manifest.json');rows=read(folder/'captures.json')
  assert manifest['error'] is None and manifest['responses']==manifest['complete']==len(rows)
  for n,h in manifest['sha256'].items():assert hashlib.sha256((folder/n).read_bytes()).hexdigest()==h
  allrows+=rows;batches.append({'label':manifest['label'],'folder':index['folder'],'chats':len(rows),'attempts':manifest['attempts'],'restored':manifest['restored']})
 assert len({x['response']['request_id'] for x in allrows})==len(allrows)
 provider=Decimal(0);trace=Decimal(0);usage=Decimal(0);summaries=[]
 for row in allrows:
  usage+=Decimal(str(row['response']['usage'].get('cost_usd') or 0))
  for sp in row['trace'].get('children',[]):
   if sp['name'] in ['llm.call','agent.summarize']:
    a=sp['attributes'];p=a.get('provider.cost_usd')
    if p is not None:provider+=Decimal(str(p))
    c=kit.span_cost(a,prices)
    if c is not None:trace+=Decimal(str(c))
    if sp['name']=='agent.summarize':summaries.append({'scenario':row['scenario'],'condition':row['condition'],'request_id':row['response']['request_id'],'session_id':row['response']['session_id'],'step':row['step'],'input':a.get('summary.input'),'output':a.get('summary.text'),'cost':c,'provider_cost':p})
 b4folder=ROOT/read(evidence/'full-b4-index.json')['folder'];b4=read(b4folder/'native-results.json')[0]['cells']
 for c in b4:c['time_ms_spread']=stats([sum(s['duration_ms'] for s in x['steps']) for x in c['results']])
 budget={}
 for profile in ['clean','lesson-08']:
  index_name=('docker-budget-'+profile+'-index.json') if (evidence/('docker-budget-'+profile+'-index.json')).exists() else ('budget-'+profile+'-index.json')
  folder=ROOT/read(evidence/index_name)['folder'];budget[profile]=read(folder/'native-results.json')
 calibration=read(evidence/'budget-calibration.json');caseid='BUD-D15'
 samples={p:next(x for x in b['cases'] if x['id']==caseid)['budget_samples'] for p,b in budget.items()}
 clean=[x['dialog_tokens'] for x in samples['clean']];defect=[x['dialog_tokens'] for x in samples['lesson-08']]
 thresholds={'too_loose':max(clean+defect)+1,'too_tight':min(clean)-1,'chosen':calibration[caseid]['thresholds']['tokens_total']}
 calibrated=[{'label':k,'threshold':v,'clean_median':statistics.median(clean),'defect_median':statistics.median(defect),'clean_pass':statistics.median(clean)<=v,'defect_pass':statistics.median(defect)<=v,'clean_individual_exceedances':sum(x>v for x in clean),'defect_individual_exceedances':sum(x>v for x in defect)} for k,v in thresholds.items()]
 result={'batches':batches,'chat_responses':len(allrows),'sessions':len({x['response']['session_id'] for x in allrows}),'provider_span_sum_usd':float(provider),'independent_all_generation_span_price_usd':float(trace),'root_usage_estimate_sum_usd':float(usage),'b4':b4,'budget_reports':budget,'calibration':calibrated,'summaries':summaries}
 write(evidence/'analysis.json',result)
 (ROOT/'l08/b4.json').write_bytes((b4folder/'native-results.json').read_bytes())
 print(json.dumps({k:result[k] for k in ['chat_responses','sessions','provider_span_sum_usd','root_usage_estimate_sum_usd']},indent=2))
if __name__=='__main__':main()
