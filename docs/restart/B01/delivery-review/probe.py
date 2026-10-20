#!/usr/bin/env python3
"""Bounded README delivery/copy/link review; no SDK or hardware execution."""
from pathlib import Path
import base64
import datetime
import hashlib
import json
import re
import subprocess
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
CANDIDATE='23ededa56620c35773247311f7ea810be643a17e'
PARTIAL='5bcfad5d6127cb53a4ca16a1e74de31c2a14f54d'
ORIGINAL='27308eb7eb80bce22f411f9d40da159d901b7087'
REVIEW='123de2ae71363b0d62d7e2240c0201539aa76075'
RESULT={'candidate':CANDIDATE,'partial_acceptance':PARTIAL,'original_documentary_candidate':ORIGINAL,
        'original_review':REVIEW,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'checks':{}}
COMMANDS=[]
def sha(data):return hashlib.sha256(data).hexdigest()
def run(args):
    p=subprocess.run(args,cwd=ROOT,capture_output=True)
    COMMANDS.append({'command':args,'exit_code':p.returncode,
       'stdout_sha256':sha(p.stdout),'stderr':p.stderr.decode(errors='replace')})
    assert p.returncode==0,(args,p.returncode)
    return p.stdout
def git(*args):return run(['git',*args])
def api(path):return json.loads(run(['gh','api',path]))
def body(commit,path):return git('show',commit+':'+path)
def tree(commit):
    rows={}
    for raw in git('ls-tree','-rz','--full-tree',commit).split(b'\0'):
        if raw:
            meta,path=raw.split(b'\t',1);rows[path.decode()]=tuple(meta.decode().split())
    return rows

try:
    current=tree(CANDIDATE);previous=tree(PARTIAL)
    assert set(current)==set(previous)
    assert sorted(p for p in current if current[p]!=previous[p])==['README.md']
    git('diff','--check',PARTIAL,CANDIDATE)
    documents=sorted(p for p in current if p.startswith('docs/restart/B01/'))
    assert len(documents)==17 and all(current[p]==previous[p] for p in documents)
    old_review=json.loads(body(CANDIDATE,'docs/restart/B01/final-review/review.json'))
    original_review=json.loads(body(REVIEW,'docs/restart/B01/final-review/review.json'))
    assert old_review==original_review
    for row in old_review['candidate_artifact_bindings']+old_review['review_artifact_bindings']:
        path=row['path'];data=body(CANDIDATE,path)
        assert len(data)==row['bytes'] and sha(data)==row['sha256']
    for name in ['report.md','review.json','verify.py','verification.json']:
        path='docs/restart/B01/final-review/'+name
        assert body(CANDIDATE,path)==body(REVIEW,path)
    accepted=json.loads(body(CANDIDATE,'docs/restart/B01/documentary-acceptance.json'))
    assert accepted['candidate_commit']==ORIGINAL and accepted['distinct_review']['commit']==REVIEW
    assert accepted['parent_criteria_closed']==0 and accepted['task_complete'] is False
    assert sha(body(CANDIDATE,accepted['distinct_review']['receipt']))==accepted['distinct_review']['sha256']
    assert all(row['parent_criterion_closed'] is False for row in old_review['criteria'])
    assert len(old_review['criteria'])==4
    assert not any(p.startswith(('crates/','examples/','tools/','.github/workflows/')) or p=='Cargo.toml' for p in current)
    readme=body(CANDIDATE,'README.md').decode();local=[];external=[]
    for raw in re.findall(r'\[[^\]\n]*\]\(([^\s)]+)\)',readme):
        url=urlsplit(raw)
        if url.scheme:external.append(raw);continue
        path=unquote(url.path)
        assert path in current and (ROOT/path).is_file()
        local.append({'path':path,'blob':current[path][2],'sha256':sha(body(CANDIDATE,path))})
    graph_url='https://github.com/nSealr/nsealr/blob/main/plan/work-items.json'
    assert graph_url in external
    graph=api('repos/nSealr/nsealr/contents/plan/work-items.json?ref=main')
    graph_data=base64.b64decode(graph['content']);plan=json.loads(graph_data)
    assert graph['html_url']==graph_url and graph['path']=='plan/work-items.json'
    assert hashlib.sha1(b'blob '+str(len(graph_data)).encode()+b'\0'+graph_data).hexdigest()==graph['sha']
    task=next(t for t in plan['tasks'] if t['id']=='B01')
    assert task['status'] not in {'verified','integrated'}
    assert task['acceptance']==[row['parent_criterion'] for row in old_review['criteria']]
    assert not task.get('result_artifacts') and not task.get('review_verdict')
    workflows=api('repos/nSealr/board-sdk/actions/workflows')
    checks=api('repos/nSealr/board-sdk/commits/'+CANDIDATE+'/check-runs')
    statuses=api('repos/nSealr/board-sdk/commits/'+CANDIDATE+'/status')
    pull=api('repos/nSealr/board-sdk/pulls/1')
    assert pull['head']['sha']==CANDIDATE
    assert workflows['total_count']==0 and workflows['workflows']==[]
    assert checks['total_count']==0 and checks['check_runs']==[] and statuses['statuses']==[]
    RESULT['candidate_tree']=git('rev-parse',CANDIDATE+'^{tree}').decode().strip()
    RESULT['checks']={'exact_delta':['README.md'],'added_or_deleted_paths':0,'changed_docs_whitespace_exit':0,
       'all17_original_B01_documents_modes_blobs_unchanged':True,
       'all4_authored_outputs_and3_review_manifest_dependencies_hash_verified':True,
       'all4_copied_original_review_files_byte_exact':True,
       'original_documentary_acceptance_receipt_unchanged_and_valid':True,
       'all4_parent_criteria_open':[{**{k:row[k] for k in ['index','parent_criterion','parent_status']},'closed':False} for row in old_review['criteria']],
       'current_authoritative_graph':{'url':graph_url,'blob':graph['sha'],'bytes':len(graph_data),'sha256':sha(graph_data),'B01_status':task['status'],'B01_criteria_unchanged':True},
       'README_local_links':local,'README_external_links':external,
       'no_executable_SDK_or_workflow_paths':True,
       'no_new_archive_bodies_or_private_sources':True,
       'actual_GitHub_observation':{'PR':1,'head':pull['head']['sha'],'draft':pull['draft'],
           'workflows':{'total_count':0,'workflows':[]},'check_runs':{'total_count':0,'check_runs':[]},
           'combined_status':{'state':statuses['state'],'statuses':[]},
           'interpretation':'No CI workflow/check/status result observed; pending aggregate with zero statuses is not a CI PASS or an executing workflow.'}}
    RESULT['outcome']='BOUNDED_README_DELIVERY_BINDINGS_VERIFIED'
except Exception as error:
    RESULT['outcome']='PROBE_FAILED';RESULT['failure']={'type':type(error).__name__,'diagnostic':str(error)}
    raise
finally:
    (OUT/'verification.json').write_text(json.dumps(RESULT,indent=2)+'\n')
    (OUT/'commands.json').write_text(json.dumps(COMMANDS,indent=2)+'\n')
