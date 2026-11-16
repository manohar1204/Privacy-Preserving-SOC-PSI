import argparse,csv,hashlib,json,platform,statistics,sys,time
from pathlib import Path
from psi import private_intersection,baseline

def fixture(n):
 def digest(prefix,i):return hashlib.sha256(f'{prefix}:{i}'.encode()).hexdigest()
 overlap=n//10
 return [digest('common',i) for i in range(overlap)]+[digest('soc',i) for i in range(n-overlap)], [digest('common',i) for i in range(overlap)]+[digest('provider',i) for i in range(n-overlap)]

def run(sizes,repeats,out):
 rows=[]
 for n in sizes:
  x,y=fixture(n); expected=baseline(x,y)
  for tb in (16,32):
   for rep in range(repeats):
    t=time.perf_counter();plain=baseline(x,y);bt=time.perf_counter()-t
    result,metrics=private_intersection(x,y,tb)
    if result!=expected or plain!=expected:raise AssertionError('intersection mismatch')
    row={'n':n,'token_bytes':tb,'repeat':rep+1,'baseline_seconds':bt,'correct':True,'match_count':len(result),**metrics}
    rows.append(row)
   print(f'n={n} token={tb} bytes: median PSI {statistics.median(r["seconds"] for r in rows if r["n"]==n and r["token_bytes"]==tb):.4f}s',flush=True)
 out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 (out.parent/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'processor':platform.processor(),'sizes':sizes,'repeats':repeats},indent=2))
 print('Saved',out)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--sizes',nargs='+',type=int,default=[100,1000,5000,10000]);p.add_argument('--repeats',type=int,default=5);p.add_argument('--out',default='results/benchmark.csv');a=p.parse_args();run(a.sizes,a.repeats,a.out)
