# project11-server
AIが補助し、ゲーム感覚で楽しく揉め事を解決するWebアプリケーション

## 開発環境の構築方法
このプロジェクトはDocker Composeを利用して動作します。基本的な作業はプロジェクトのルートディレクトリで行います。

### 事前準備
`.env.dist` ファイルを `.env` にコピーしてください。

### ローカルサーバーの起動
以下のコマンドでイメージのビルドとコンテナの起動が行われ、ローカルサーバーが立ち上がります。

```bash
make dev
```

- Django: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:9000](http://localhost:9000)

### API仕様書の確認方法  
APIの仕様だけを確認したい場合は、[Swagger Editor](https://editor-next.swagger.io/) に `openapi/main.yaml` の内容をコピー＆ペーストしてください。
