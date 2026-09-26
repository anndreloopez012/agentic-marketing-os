#!/usr/bin/env python3
"""Read-only external integration envelopes and canonical portable task model."""
from __future__ import annotations
import datetime as dt, hashlib, json, re, subprocess
from pathlib import Path
from portable_paths import CONFIG_ROOT, DATA_ROOT, MEMORIA_ROOT
ROOT=DATA_ROOT/'integrations'; TASKS=DATA_ROOT/'tasks.json'; TASK_NOTES=MEMORIA_ROOT/'Tareas'; REPORT=MEMORIA_ROOT/'Integraciones'/'Estado de Integraciones.md'
def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8'))
 except:return d
def gh_snapshot():
 try:
  p=subprocess.run(['gh','api','search/issues','--method','GET','-f','q=is:open assignee:@me','-f','per_page=100'],capture_output=True,text=True,timeout=45,check=True); raw=json.loads(p.stdout)
  return {'status':'connected-read-only','updated_at':dt.datetime.now().astimezone().isoformat(timespec='seconds'),'items':[{'id':str(x['id']),'number':x['number'],'title':x['title'],'url':x['html_url'],'state':x['state'],'repository':x.get('repository_url','').split('/repos/')[-1],'kind':'pull-request' if 'pull_request' in x else 'issue','updated_at':x['updated_at']} for x in raw.get('items',[])]}
 except Exception as e:return {'status':'error','error':str(e),'items':[]}
def local_tasks():
 rows=[]
 for p in MEMORIA_ROOT.rglob('*.md'):
  if 'Graphify' in p.parts or 'Templates' in p.parts:continue
  for n,line in enumerate(p.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
   m=re.match(r'^\s*- \[([ xX])\]\s+(.+)$',line)
   if not m:continue
   title=m.group(2).strip(); identity=hashlib.sha1(f'{p.relative_to(MEMORIA_ROOT)}:{n}:{title}'.encode()).hexdigest()[:14]
   due=(re.search(r'📅\s*(20\d{2}-\d{2}-\d{2})',title) or re.search(r'\bdue::\s*(20\d{2}-\d{2}-\d{2})',title))
   rows.append({'task_id':'obs-'+identity,'title':title,'status':'done' if m.group(1).lower()=='x' else 'open','priority':'normal','due':due.group(1) if due else None,'project':None,'provider':'obsidian','external_id':None,'external_url':None,'authority':'obsidian','sync_mode':'local','source':str(p.relative_to(MEMORIA_ROOT)),'line':n})
 return rows
def main():
 ROOT.mkdir(parents=True,exist_ok=True); TASK_NOTES.mkdir(parents=True,exist_ok=True); now=dt.datetime.now().astimezone().isoformat(timespec='seconds')
 github=gh_snapshot(); (ROOT/'github.json').write_text(json.dumps(github,ensure_ascii=False,indent=2),encoding='utf-8')
 linear=load(ROOT/'linear.json',{'status':'connector-ready-no-envelope','items':[]}); calendar=load(ROOT/'calendar.json',{'status':'reauth-required-invalid_grant','items':[]})
 tasks=local_tasks()
 for x in github.get('items',[]): tasks.append({'task_id':'github-'+x['id'],'title':x['title'],'status':x['state'],'priority':'normal','due':None,'project':x['repository'],'provider':'github','external_id':x['number'],'external_url':x['url'],'authority':'github','sync_mode':'read-only','last_synced_at':now})
 for x in linear.get('items',[]): tasks.append({'task_id':'linear-'+x['id'],'title':x['title'],'status':x.get('status','unknown'),'priority':x.get('priority','normal'),'due':x.get('dueDate'),'project':x.get('project'),'provider':'linear','external_id':x['id'],'external_url':x.get('url'),'authority':'linear','sync_mode':'read-only','last_synced_at':linear.get('updated_at')})
 TASKS.write_text(json.dumps({'version':1,'updated_at':now,'tasks':tasks},ensure_ascii=False,indent=2),encoding='utf-8')
 for old in TASK_NOTES.glob('*.md'):
  if old.name!='README.md':old.unlink()
 for t in tasks:
  if t['provider']=='obsidian':continue
  body=f'---\ntipo: tarea-externa\ntask_id: "{t["task_id"]}"\nproveedor: "{t["provider"]}"\nestado: "{t["status"]}"\nprioridad: "{t["priority"]}"\nautoridad: "{t["authority"]}"\nsync_mode: "read-only"\nexternal_id: "{t["external_id"]}"\ngenerado: true\n---\n\n# {t["title"]}\n\n- Enlace externo: {t.get("external_url") or "No disponible"}\n- La edición externa requiere una orden explícita; esta nota es un espejo de solo lectura.\n'
  (TASK_NOTES/f'{t["task_id"]}.md').write_text(body,encoding='utf-8')
 statuses={'github':github.get('status'),'linear':linear.get('status'),'calendar':calendar.get('status'),'tasks':'active'}
 lines=['---\ntipo: estado-integraciones\nestado: activo\ngenerado: true\ntags:\n  - memoria\n  - integraciones\n---\n\n# Estado de Integraciones\n\n',f'- Actualizado: `{now}`\n- GitHub: **{statuses["github"]}** · {len(github.get("items",[]))} elementos\n- Linear: **{statuses["linear"]}** · {len(linear.get("items",[]))} elementos\n- Calendario: **{statuses["calendar"]}** · {len(calendar.get("items",[]))} eventos\n- Tareas canónicas: **{len(tasks)}**\n\n## Autoridad\nTodos los conectores están en lectura. Ninguna tarea, issue o evento se crea/modifica/cierra sin una orden explícita. OAuth y tokens permanecen fuera del Vault.\n']
 REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text(''.join(lines),encoding='utf-8'); print(f'Integrations: {statuses}; tasks={len(tasks)}')
if __name__=='__main__':main()
