import os
import requests

def configured():
    return bool(os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

def headers():
    key=os.environ['SUPABASE_SERVICE_ROLE_KEY']
    return {'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'}

def fetch_posts():
    if not configured(): return []
    base=os.environ['SUPABASE_URL'].rstrip('/')+'/rest/v1/posts'
    out=[]; offset=0
    while offset<10000:
        response=requests.get(base,headers=headers(),params={'select':'id,created_at,text,url,prefecture,carrier,benefit,amount,model,collected_at','order':'created_at.desc','limit':1000,'offset':offset},timeout=30)
        response.raise_for_status()
        batch=response.json();out.extend(batch)
        if len(batch)<1000:break
        offset+=1000
    return out

def save_posts(posts):
    if not posts:return 0
    if not configured():raise RuntimeError('Supabase環境変数が未設定です')
    base=os.environ['SUPABASE_URL'].rstrip('/')+'/rest/v1/posts?on_conflict=id'
    response=requests.post(base,headers={**headers(),'Prefer':'resolution=merge-duplicates,return=minimal'},json=posts,timeout=45)
    response.raise_for_status()
    return len(posts)
