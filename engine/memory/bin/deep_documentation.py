#!/usr/bin/env python3
"""Incremental evidence-first deep indexing for every Markdown document."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, re
from pathlib import Path
from portable_paths import DATA_ROOT, GRAPH_ROOT, MEMORIA_ROOT, VAULT_ROOT

STATE=DATA_ROOT/'deep_docs_index.json'; REPORT=MEMORIA_ROOT/'Reportes'/'Procesamiento Profundo de Documentos.md'
EXTRACTOR='graph-assisted-deterministic-v2'
SKIP={'Graphify','Templates'}
SECRET_PATTERNS=(
 re.compile(r'(?i)(password|token|secret|api[_-]?key)\s*[:=]\s*\S+'),
 re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
 re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b'), re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
 re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{20,}\b'),
 re.compile(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b'),
 re.compile(r'(?i)\b[a-z][a-z0-9+.-]*://[^\s/:]+:[^\s/@]+@[^\s]+'),
)
def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8'))
 except:return d
def words(text): return len(re.findall(r'\b\w+\b',text))
def portable_text(text):
 text=text.replace(str(VAULT_ROOT),'$VAULT_ROOT')
 text=re.sub(r'/Users/[^/\s]+/Documents/PROYECTOS', '$PROJECTS_ROOT', text)
 text=re.sub(r'/Users/[^/\s]+/Documents/Playground', '$PLAYGROUND_ROOT', text)
 text=re.sub(r'/Users/[^/\s]+', '$USER_HOME', text)
 return text
def graph_sources(graph):
 result=set()
 for node in graph.get('nodes',[]):
  if not isinstance(node,dict): continue
  source=str(node.get('source_file') or node.get('source') or '').replace('\\','/').lstrip('./')
  if source: result.add(source)
 return result
def analyze(path, graph_sources):
 raw=path.read_text(encoding='utf-8',errors='ignore'); clean=raw
 for pattern in SECRET_PATTERNS: clean=pattern.sub('[REDACTADO]',clean)
 clean=portable_text(clean); digest=hashlib.sha256(raw.encode()).hexdigest()
 heads=[m.group(2).strip() for m in re.finditer(r'(?m)^(#{1,4})\s+(.+)$',clean)][:40]
 tasks=[m.group(1).strip() for m in re.finditer(r'(?m)^\s*- \[ \]\s+(.+)$',clean)][:30]
 links=[m.group(1).split('|')[0] for m in re.finditer(r'\[\[([^\]]+)\]\]',clean)][:50]
 dates=sorted(set(re.findall(r'\b20\d{2}-\d{2}-\d{2}\b',clean)))[:30]
 summary=' '.join(re.sub(r'[`#>*_\[\]]',' ',clean).split())[:700]
 relative=str(path.relative_to(VAULT_ROOT)).replace('\\','/')
 return {'path':relative,'sha256':digest,'words':words(clean),'headings':heads,'tasks':tasks,'links':links,'dates':dates,'summary':summary,'graph_indexed':relative in graph_sources,'evidence':f'{relative}:1','extractor':EXTRACTOR,'confidence':'high','llm_enrichment':'pending-no-provider-key'}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--force',action='store_true'); ap.add_argument('--limit',type=int,default=0); a=ap.parse_args()
 old=load(STATE,{'documents':{}}); graph=load(GRAPH_ROOT/'graph.json',{}); sources=graph_sources(graph)
 paths=[p for p in MEMORIA_ROOT.rglob('*.md') if not any(x in p.parts for x in SKIP) and p!=REPORT]
 if a.limit: paths=paths[:a.limit]
 docs={}; changed=0
 for p in paths:
  key=str(p.relative_to(VAULT_ROOT)); digest=hashlib.sha256(p.read_bytes()).hexdigest(); prev=old.get('documents',{}).get(key)
  if prev and prev.get('sha256')==digest and prev.get('extractor')==EXTRACTOR and not a.force: docs[key]=prev
  else: docs[key]=analyze(p,sources); changed+=1
 now=dt.datetime.now().astimezone().isoformat(timespec='seconds'); payload={'version':1,'updated_at':now,'document_count':len(docs),'changed':changed,'provider':'graphify+deterministic','llm_status':'ready-when-GEMINI_API_KEY-or-GOOGLE_API_KEY-is-set','documents':docs}; STATE.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
 total=sum(x['words'] for x in docs.values()); pending=sum(bool(x['tasks']) for x in docs.values()); connected=sum(bool(x.get('graph_indexed')) for x in docs.values())
 lines=['---\ntipo: reporte-procesamiento-profundo\nestado: activo\ngenerado: true\ntags:\n  - memoria\n  - ia\n  - documentos\n---\n\n# Procesamiento Profundo de Documentos\n\n',f'- Documentos analizados: **{len(docs)}**\n- Palabras indexadas: **{total}**\n- Modificados en esta corrida: **{changed}**\n- Documentos enlazados a Graphify: **{connected}**\n- Documentos con tareas: **{pending}**\n- Extracción actual: **Graphify + análisis determinístico con evidencia**\n- Enriquecimiento LLM: **preparado; requiere `GEMINI_API_KEY` fuera del Vault**\n\n## Trazabilidad\nCada registro conserva SHA-256, fuente, encabezados, fechas, enlaces, tareas, extractor y confianza en `.memoria-system/data/deep_docs_index.json`.\n\n## Documentos recientes o cambiados\n']
 for item in sorted(docs.values(),key=lambda x:x['path'])[:150]: lines.append(f"- `{item['path']}` · {item['words']} palabras · evidencia `{item['evidence']}`\n")
 REPORT.write_text(''.join(lines),encoding='utf-8'); print(f'Deep docs: {len(docs)} documentos; changed={changed}; words={total}')
if __name__=='__main__': main()
