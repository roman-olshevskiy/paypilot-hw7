"""Docker native CLI capture; parent verified Git forecast before creating clone."""
import os,sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from hw7_capture import Capture,write
import stand,runner,cli

def main():
 assert os.environ.get('HW7_PAID')=='1'
 assert hashlib.sha256((ROOT/'l08/forecast-before-runs.md').read_bytes()).hexdigest()==os.environ['HW7_FORECAST_SHA']
 frozen=json.loads((ROOT/'evidence/budget-freeze.json').read_text(encoding='utf-8'))
 assert hashlib.sha256((ROOT/'sets/l05_dialogs.jsonl').read_bytes()).hexdigest()==frozen['sha256']
 args=sys.argv[1:];profile=args[args.index('--profile')+1];label='docker-budget-'+profile;cap=Capture(label,stand);original=runner.run_case
 def case(c):
  cap.context={'scenario':c['id'],'condition':label,'settings':json.loads(os.environ.get('STAND_SETTINGS','{}'))};cap.repeat=0
  return original(c)
 runner.run_case=case
 def execute():
  before=set((ROOT/'reports').glob('*.json'));code=cli.main(args)
  for p in set((ROOT/'reports').glob('*.json'))-before:(cap.folder/'native-results.json').write_bytes(p.read_bytes())
  if code not in (0,1):raise RuntimeError('Native CLI error '+str(code))
  return code
 cap.execute(label,execute)
 write(ROOT/('evidence/'+label+'-index.json'),{'folder':cap.folder.relative_to(ROOT).as_posix()})
if __name__=='__main__':main()
