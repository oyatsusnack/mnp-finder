import sqlite3
import pandas as pd
import streamlit as st
from collector import DB,init,PREFS
from storage import configured,fetch_posts
st.set_page_config(page_title='MNP特典サーチ',page_icon='📱',layout='wide')
st.title('📱 MNP特典サーチ')
st.caption('X投稿を都道府県・キャリア・特典で検索。投稿内容は未検証です。')
init()
with st.sidebar:
 st.header('検索条件')
 pref=st.selectbox('都道府県',['すべて']+[p+('都' if p=='東京' else '府' if p in ('大阪','京都') else '' if p=='北海道' else '県') for p in PREFS]+['地域不明'])
 carrier=st.selectbox('キャリア',['すべて','ドコモ','au','ソフトバンク','楽天モバイル','UQ mobile','ワイモバイル','ahamo','LINEMO','IIJmio','不明'])
 benefit=st.selectbox('特典内容',['すべて','一括1円','一括特価','実質1円','キャッシュバック','ポイント還元','商品券','端末割引','その他'])
 keyword=st.text_input('機種・店舗・キーワード')
 order=st.selectbox('並び順',['投稿が新しい順','金額が高い順'])
 st.caption('投稿収集はサーバー側の定期ジョブで実行します。')
if configured():
 try: df=pd.DataFrame(fetch_posts(),columns=['id','created_at','text','url','prefecture','carrier','benefit','amount','model','collected_at'])
 except Exception as e:
  st.error('データ取得に失敗しました。管理者に接続設定の確認を依頼してください。');st.stop()
else:
 with sqlite3.connect(DB) as db:
  df=pd.read_sql_query('SELECT created_at, prefecture, carrier, benefit, amount, model, text, url FROM posts',db)
if df.empty:
 st.info('まだ投稿データがありません。X API認証を設定して collector.py を実行してください。')
else:
 if pref!='すべて':df=df[df.prefecture==pref]
 if carrier!='すべて':df=df[df.carrier==carrier]
 if benefit!='すべて':df=df[df.benefit==benefit]
 if keyword:df=df[df[['text','model']].fillna('').apply(lambda col:col.str.contains(keyword,case=False,regex=False)).any(axis=1)]
 df=df.sort_values('amount' if order=='金額が高い順' else 'created_at',ascending=False,na_position='last')
 st.metric('該当投稿',f'{len(df):,}件')
 st.dataframe(df.rename(columns={'created_at':'投稿日時 (UTC)','prefecture':'都道府県','carrier':'キャリア','benefit':'特典','amount':'抽出金額（参考）','model':'機種','text':'投稿本文','url':'X投稿'}),hide_index=True,use_container_width=True,column_config={'X投稿':st.column_config.LinkColumn('X投稿',display_text='投稿を見る')})
 st.download_button('検索結果をCSV保存',df.to_csv(index=False).encode('utf-8-sig'),'mnp_results.csv','text/csv')
st.warning('金額は投稿文からの機械抽出で、還元額・端末価格・条件を区別できない場合があります。特典の有効性や在庫、契約条件は元投稿・店舗で確認してください。')
st.divider()
st.subheader('📝 MNP特典情報の登録')
post_text = st.text_area('MNP特典の投稿内容')
if st.button('登録する'):
     st.info('登録機能は準備中です')
