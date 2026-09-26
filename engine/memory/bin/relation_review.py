#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json
from pathlib import Path
from portable_paths import CONFIG_ROOT, DATA_ROOT, MEMORIA_ROOT
DEPS=DATA_ROOT/'project_dependencies.json'; PROPOSALS=DATA_ROOT/'relation_proposals.json'; HISTORY=DATA_ROOT/'relation_decisions.jsonl'; OVERRIDES=CONFIG_ROOT/'dependency_overrides.json'; ROOT=MEMORIA_ROOT/'Relaciones'/'Por confirmar'
def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8'))
 except:return d
def rid(x):return hashlib.sha1(f"{x['source']}|{x['target']}|{x['evidence']}".encode()).hexdigest()[:12]
def build():
 deps=load(DEPS,{}).get('dependencies',[]); old=load(PROPOSALS,{}).get('relations',{}); rels={}
 ROOT.mkdir(parents=True,exist_ok=True)
 for d in deps:
  i=rid(d); status='confirmed' if d['kind']=='confirmed' else old.get(i,{}).get('status','proposed'); r={**d,'relation_id':i,'status':status}; rels[i]=r
  if status=='proposed': (ROOT/f'{i}.md').write_text(f'---\ntipo: relacion-propuesta\nrelation_id: "{i}"\norigen: "{d["source"]}"\ndestino: "{d["target"]}"\nestado: propuesta\nconfianza: "{d["confidence"]}"\ngenerado: true\n---\n\n# {d["source"]} → {d["target"]}\n\n- Evidencia: {d["evidence"]}\n- Origen: `{d["origin"]}`\n\n## Revisión\n- [ ] Confirmar en código o configuración.\n- [ ] Registrar motivo de confirmación o rechazo.\n',encoding='utf-8')
 PROPOSALS.write_text(json.dumps({'version':1,'relations':rels},ensure_ascii=False,indent=2),encoding='utf-8'); index=MEMORIA_ROOT/'Relaciones'/'Relaciones por Confirmar.md'; index.parent.mkdir(parents=True,exist_ok=True); index.write_text('# Relaciones por Confirmar\n\n'+''.join(f'- [[Por confirmar/{i}|{r["source"]} → {r["target"]}]] · {r["confidence"]}\n' for i,r in rels.items() if r['status']=='proposed'),encoding='utf-8'); return rels
def decide(i,status,reason):
 rels=build(); r=rels.get(i)
 if not r:raise SystemExit('Relación no encontrada')
 over=load(OVERRIDES,{'confirmed':[],'ignored':[]}); key=lambda x:(x.get('source'),x.get('target'))
 over['confirmed']=[x for x in over['confirmed'] if key(x)!=key(r)]; over['ignored']=[x for x in over['ignored'] if key(x)!=key(r)]
 if status=='confirmed':over['confirmed'].append({'source':r['source'],'target':r['target'],'evidence':reason or r['evidence']})
 else:over['ignored'].append({'source':r['source'],'target':r['target'],'reason':reason})
 OVERRIDES.write_text(json.dumps(over,ensure_ascii=False,indent=2),encoding='utf-8'); event={'relation_id':i,'status':status,'reason':reason,'decided_at':dt.datetime.now().astimezone().isoformat(timespec='seconds'),'decided_by':'user-via-memoria'}
 r['status']=status; rels[i]=r; PROPOSALS.write_text(json.dumps({'version':1,'relations':rels},ensure_ascii=False,indent=2),encoding='utf-8'); (ROOT/f'{i}.md').unlink(missing_ok=True)
 with HISTORY.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n'); print(json.dumps(event,ensure_ascii=False))
def main():
 ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd'); sub.add_parser('build'); p=sub.add_parser('confirm');p.add_argument('id');p.add_argument('--reason',default=''); p=sub.add_parser('reject');p.add_argument('id');p.add_argument('--reason',required=True); a=ap.parse_args()
 if a.cmd=='confirm':decide(a.id,'confirmed',a.reason)
 elif a.cmd=='reject':decide(a.id,'rejected',a.reason)
 else: print(f'Relaciones propuestas: {sum(r["status"]=="proposed" for r in build().values())}')
if __name__=='__main__':main()
