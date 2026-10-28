import os, re, sqlite3, datetime, requests
from pathlib import Path
from storage import configured, save_posts
DB = Path(os.getenv('MNP_DB','mnp.sqlite3'))
PREFS = '北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄'.split()
CARRIERS = {'ドコモ':['ドコモ','docomo','ドコモショップ'],'au':['au','エーユー'],'ソフトバンク':['ソフトバンク','softbank'],'楽天モバイル':['楽天モバイル'],'UQ mobile':['UQ mobile','UQモバイル'],'ワイモバイル':['ワイモバイル','Y!mobile'],'ahamo':['ahamo'],'LINEMO':['LINEMO'],'IIJmio':['IIJmio']}
BENEFITS = {'一括1円':r'一括\s*1\s*円','一括特価':r'一括(?:特価|価格|\s*\d[\d,]*\s*円)','実質1円':r'実質\s*1\s*円','キャッシュバック':r'キャッシュバック|\bCB\b','ポイント還元':r'ポイント|\bpt\b|還元','商品券':r'商品券|ギフト券','端末割引':r'値引|割引|特価'}
def init():
 with sqlite3.connect(DB) as db:
  db.execute('CREATE TABLE IF NOT EXISTS posts (id TEXT PRIMARY KEY, created_at TEXT, text TEXT, url TEXT, prefecture TEXT, carrier TEXT, benefit TEXT, amount INTEGER, model TEXT, collected_at TEXT)')
def extract(t):
 prefs=[p+('都' if p=='東京' else '府' if p in ('大阪','京都') else '' if p=='北海道' else '県') for p in PREFS]
 prefecture=next((p for p in prefs if p in t), '地域不明')
 lower=t.lower()
 carrier=next((k for k,terms in CARRIERS.items() if any(x.lower() in lower for x in terms)), '不明')
 benefit=next((k for k,pattern in BENEFITS.items() if re.search(pattern,t,re.I)), 'その他')
 amounts=[int(x.replace(',','')) for x in re.findall(r'([\d,]{3,7})\s*(?:円|pt|ポイント)',t,re.I)]
 model=next((m.group(0) for pattern in [r'iPhone\s*\d{2}(?:\s*(?:Pro Max|Pro|Plus|e))?',r'Pixel\s*\d{1,2}[a-zA-Z ]*',r'Galaxy\s*[A-Z]\d{2}[a-zA-Z]*',r'AQUOS\s*[\w-]+'] if (m:=re.search(pattern,t,re.I))), '機種不明')
 return prefecture,carrier,benefit,max(amounts,default=None),model

def collect(max_pages=3):
 token=os.getenv('X_BEARER_TOKEN')
 if not token: raise RuntimeError('環境変数 X_BEARER_TOKEN を設定してください')
 init(); total=0; remote_posts=[]
 queries=['(MNP OR 乗り換え) (一括 OR 特価 OR キャッシュバック) lang:ja -is:retweet','(MNP OR 乗り換え) (ポイント還元 OR 商品券 OR 割引) lang:ja -is:retweet']
 with sqlite3.connect(DB) as db:
  for query in queries:
   next_token=None
   for _ in range(max_pages):
    params={'query':query,'max_results':100,'tweet.fields':'created_at'}
    if next_token:params['next_token']=next_token
    resp=requests.get('https://api.x.com/2/tweets/search/recent',headers={'Authorization':f'Bearer {token}'},params=params,timeout=30)
    resp.raise_for_status(); payload=resp.json()
    for post in payload.get('data',[]):
     t=post['text']; pref,carrier,benefit,amount,model=extract(t)
     row=(post['id'],post.get('created_at',''),t,f"https://x.com/i/web/status/{post['id']}",pref,carrier,benefit,amount,model,datetime.datetime.now(datetime.timezone.utc).isoformat())
     db.execute('INSERT OR IGNORE INTO posts VALUES (?,?,?,?,?,?,?,?,?,?)',row)
     remote_posts.append(dict(zip(('id','created_at','text','url','prefecture','carrier','benefit','amount','model','collected_at'),row)))
     total+=1
    next_token=payload.get('meta',{}).get('next_token')
    if not next_token:break
 if configured():
  for start in range(0,len(remote_posts),200):save_posts(remote_posts[start:start+200])
 return total
if __name__=='__main__':print('取得件数:',collect())
