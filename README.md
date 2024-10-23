# project11-server
AIが補助し、ゲーム感覚で楽しく揉め事を解決するWebアプリケーション

## 開発環境の構築方法
このプロジェクトはDocker Composeを利用して動作します。基本的な作業はプロジェクトのルートディレクトリで行います。

### 事前準備
`.env.dev` ファイルを `.env` にコピーしてください。
```bash
cp .env.dev .env
```

### ローカルサーバーの起動
以下のコマンドでイメージのビルドとコンテナの起動が行われ、ローカルサーバーが立ち上がります。

```bash
make dev
```

- Django: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:9000](http://localhost:9000)

### API仕様書の確認方法  
APIの仕様だけを確認したい場合は、[Swagger Editor](https://editor-next.swagger.io/) に `openapi/main.yaml` の内容をコピー＆ペーストしてください。

### Djangoが立ち上がらないとき（バックエンド以外向け）
dbフォルダを削除してから，`make dev`で新しく環境を立ち上げると治る可能性があります．
