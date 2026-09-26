#!/usr/bin/env python3
"""Append-only temporal history for the current Graphify master graph."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json
from collections import Counter
from pathlib import Path
from portable_paths import DATA_ROOT, GRAPH_ROOT, MEMORIA_ROOT
STATE=DATA_ROOT/'temporal_graph.json'; EVENTS=DATA_ROOT/'graph_events.jsonl'; REPORT=MEMORIA_ROOT/'Graphify'/'Linea de Tiempo.md'
def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8'))
 except:return d
def canon(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read_events():
 all_events=[]
 if EVENTS.exists():
  for line in EVENTS.read_text(encoding='utf-8').splitlines():
   try: all_events.append(json.loads(line))
   except (json.JSONDecodeError, TypeError): pass
 return all_events
def main():
 parser=argparse.ArgumentParser(description='Historial temporal append-only del grafo maestro')
 parser.add_argument('--since',help='Mostrar eventos desde YYYY-MM-DD')
 parser.add_argument('--project',help='Filtrar por proyecto, origen o entidad')
 parser.add_argument('--json',action='store_true',help='Emitir la consulta como JSON')
 args=parser.parse_args()
 if args.since or args.project or args.json:
  selected=read_events()
  if args.since: selected=[e for e in selected if str(e.get('observed_at',''))[:10]>=args.since]
  if args.project:
   needle=args.project.casefold(); selected=[e for e in selected if needle in json.dumps(e,ensure_ascii=False).casefold()]
  if args.json: print(json.dumps(selected,ensure_ascii=False,indent=2))
  else:
   print(f'Historia: {len(selected)} evento(s) coinciden')
   for e in selected[-100:]: print(f"{e['observed_at']} | {e['action']} | {e['entity_type']} | {e['entity_id']}")
  return
 graph=load(GRAPH_ROOT/'graph.json',{}); old=load(STATE,{'entities':{}}); now=dt.datetime.now().astimezone().isoformat(timespec='seconds')
 previous_events=read_events(); removed_before={e['entity_id'] for e in previous_events if e.get('action')=='removed'}
 current={}
 for kind,items in [('node',graph.get('nodes',[])),('edge',graph.get('links',graph.get('edges',[])))]:
  for item in items:
   identity=str(item.get('id') or f"{item.get('source')}|{item.get('target')}|{item.get('relation') or item.get('type')}")
   key=f'{kind}:{identity}'; current[key]={'kind':kind,'id':identity,'hash':canon(item),'source':item.get('source_file') or item.get('source') or ''}
 prior=old.get('entities',{}); events=[]
 for key,item in current.items():
  action=('restored' if item['id'] in removed_before else 'added') if key not in prior else ('changed' if prior[key].get('hash')!=item['hash'] else None)
  if action: events.append({'event_id':hashlib.sha1(f'{now}|{action}|{key}'.encode()).hexdigest(),'entity_type':item['kind'],'entity_id':item['id'],'action':action,'observed_at':now,'valid_from':now,'valid_to':None,'content_hash':item['hash'],'source':item['source']})
 for key,item in prior.items():
  if key not in current: events.append({'event_id':hashlib.sha1(f'{now}|removed|{key}'.encode()).hexdigest(),'entity_type':item['kind'],'entity_id':item['id'],'action':'removed','observed_at':now,'valid_from':item.get('valid_from'),'valid_to':now,'content_hash':item['hash'],'source':item.get('source','')})
 if events:
  with EVENTS.open('a',encoding='utf-8') as f:
   for e in events:f.write(json.dumps(e,ensure_ascii=False)+'\n')
 for item in current.values(): item['valid_from']=prior.get(f"{item['kind']}:{item['id']}",{}).get('valid_from',now)
 STATE.write_text(json.dumps({'version':1,'updated_at':now,'entities':current},ensure_ascii=False,indent=2),encoding='utf-8')
 all_events=read_events()
 counts={a:sum(e['action']==a for e in all_events) for a in ('added','changed','removed','restored')}
 by_day=Counter(str(e.get('observed_at',''))[:10] for e in all_events)
 lines=['---\ntipo: grafo-temporal\nestado: activo\ngenerado: true\ntags:\n  - memoria\n  - graphify\n  - temporal\n---\n\n# Línea de Tiempo del Grafo\n\n',f'- Entidades actuales: **{len(current)}**\n- Eventos históricos: **{len(all_events)}**\n- Esta corrida: **{len(events)}**\n- Acumulado: `{counts}`\n- Consulta: `memoria historia [proyecto] --desde YYYY-MM-DD`\n\n## Comparación por fecha\n']
 for day,total in sorted(by_day.items(),reverse=True)[:30]:
  day_events=[e for e in all_events if str(e.get('observed_at','')).startswith(day)]
  day_counts=Counter(e.get('action') for e in day_events)
  lines.append(f"- **{day}** · {total} eventos · +{day_counts['added']} · ~{day_counts['changed']} · -{day_counts['removed']} · ↺{day_counts['restored']}\n")
 lines.append('\n## Eventos recientes\n')
 for e in reversed(all_events[-100:]): lines.append(f"- `{e['observed_at']}` · **{e['action']}** · `{e['entity_type']}` · `{str(e['entity_id'])[:100]}`\n")
 REPORT.write_text(''.join(lines),encoding='utf-8')
 print(f'Temporal graph: current={len(current)} events={len(events)} total={len(all_events)}')
if __name__=='__main__':main()
