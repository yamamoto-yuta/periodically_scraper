# periodically_scraper

定期スクレイピングプログラム

## 初回の環境構築

### Clone と Build

```
$ git clone <REPOSITORY_URL>
$ cd ./periodically_scraper/
$ docker-compose build
```

### Google 認証ファイルの作成

1. 「Google Cloud > API とサービス > 認証情報」から認証情報を取得し， `client_secrets.json` という名前でリポジトリ直下に保存する

2. Google ドライブとの認証を行う．認証は Docker コンテナ内の Python で次のコードを実行することで行える

```python
>>> from periodically_scraper.shared.gdrive_client import GDriveClient
>>> gdrive = GDriveClient()
```

> 参考：[Docker+Python 環境から Google ドライブへアクセスする - Qiita](https://qiita.com/yamamoto-yuta/items/870d198a66476c1dea4a)

### 環境変数の設定

1. `.env.sample` をコピー
2. 各種環境変数を設定する

## 環境の立ち上げ

```
$ docker-compose up -d
```

## スクレイピングするサイトを増やすときは

1. Google ドライブの `html/` にサイトのドメイン名でフォルダを作る
2. `services/` にスクレイピングコードを実装する
3. `save-article.yml` に実装したコードの実行コマンドを追加する

## 既知の問題

### Google ドライブとの認証が 1 時間で切れる

#### どういうこと？

Google ドライブの操作に利用しているサービスアカウントのデフォルトの有効時間は 1 時間のため、有効時間を変更していないと実行から 1 時間後に認証エラーで処理が落ちてしまう

> 参考：[有効期間が短いサービス アカウント認証情報の作成 | IAM のドキュメント | Google Cloud](https://cloud.google.com/iam/docs/creating-short-lived-service-account-credentials?hl=ja#sa-credentials-oauth)
