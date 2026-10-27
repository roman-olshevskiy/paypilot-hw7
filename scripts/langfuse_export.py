"""Documented local Langfuse API export, no model calls."""
import json,urllib.request,urllib.parse,base64,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUTH='Basic '+base64.b64encode(b'pk-lf-paypilot-local:sk-lf-paypilot-local').decode()
def api(path,data=None):
 req=urllib.request.Request('http://localhost:3000/api/public'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Authorization':AUTH,'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=60) as response:return json.load(response)
def export(session):
 rows=[];cursor=None
 while True:
  params={'sessionId':session,'fields':'core,basic,model,usage,metrics,io,metadata,trace_context','limit':1000}
  if cursor:params['cursor']=cursor
  result=api('/v2/observations?'+urllib.parse.urlencode(params));rows+=result['data'];cursor=result.get('meta',{}).get('cursor')
  if not cursor:break
 out=ROOT/'evidence/langfuse'/('session-'+session+'.json');out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
 print('Exported',len(rows),'observations for',session)
 return rows
if __name__=='__main__':export(sys.argv[1])
