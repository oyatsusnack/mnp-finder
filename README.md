# MNP特典サーチ — iPhone対応Web公開版

Streamlit Community Cloud + Supabase + GitHub Actions で、スマホのSafariからアクセスできるMNP特典検索アプリです。

## 公開手順

1. GitHubで**private**リポジトリを作り、このフォルダのファイル（隠しフォルダ `.github` と `.streamlit` を含む）をアップロードします。GitHub Actionsが利用可能な設定にしてください。
2. Supabaseでプロジェクトを作り、SQL Editorで `schema.sql` を実行します。Project URLと**service_role**キーを取得します。service_roleキーは絶対にWeb画面や公開リポジトリに貼らないでください。
3. X Developer Portalで利用可能なX APIプランを確認し、Bearer Tokenを発行します。X APIには利用料金・検索期間・件数制限があり、収集量は契約に依存します。
4. GitHubのSettings → Secrets and variables → Actionsで `X_BEARER_TOKEN`、`SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY` の3つを登録します。
5. GitHubのActionsタブから「Collect MNP posts」を手動実行して、Supabaseの `posts` にデータが入ることを確認します。以降は6時間ごとに実行を試みます（GitHub Actionsのスケジュール実行は遅延・停止する場合があります）。
6. [Streamlit Community Cloud](https://share.streamlit.io/) でGitHubリポジトリを接続し、Entry pointに `app.py` を指定してデプロイします。**privateリポジトリの利用可否や公開設定はプランを確認してください。**
7. StreamlitアプリのSettings → Secretsに以下を登録します（`X_BEARER_TOKEN`はアプリ側には不要）。

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "YOUR_SERVICE_ROLE_KEY"
```

8. 発行された `https://....streamlit.app` URLをiPhoneのSafariで開き、共有 →「ホーム画面に追加」を選ぶとアプリ風に使えます。

## ローカルで試す

```bash
pip install -r requirements.txt
streamlit run app.py
```

ローカルで収集する場合は `X_BEARER_TOKEN` を環境変数に設定して `python collector.py` を実行します。Supabaseの2つの環境変数がある場合はリモートDBにも保存します。未設定の場合はSQLiteを使います。

## セキュリティと制約

- service_roleキーはデータベースの強い権限を持ちます。GitHub SecretsとStreamlit Secretsにのみ保存し、画面・ログ・公開ソースに露出させないでください。公開アプリでこの構成を使う場合、Streamlitのサーバー側でのみ呼び出す設計です。
- アプリは最新10,000投稿まで表示します。全件検索が必要ならサーバー側ページネーションに変更してください。
- 投稿の地域・金額・特典判定は簡易的で誤判定があり、開催中である保証はありません。投稿・店舗で条件を必ず確認してください。
- Xの検索API仕様・価格・利用規約と、Streamlit/Supabase/GitHubの無料枠・利用規約は変更され得ます。
- 公開URLは手順を完了した後に発行されます。このZIPだけではWeb公開は完了しません。
