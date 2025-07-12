# Restaurant Recommendation API

## 概要

AIヒアリング機能付きレストラン推薦システムです。少人数グループが外食先を決定する際、OpenAI GPT-3.5を活用して個別にヒアリングを行い、全員にとって最適な飲食店を推薦するサービスのバックエンドAPIです。

## 主な機能

- 🤖 **AIヒアリング**: OpenAI GPT-3.5-turboによる自然な対話
- 👥 **匿名グループ**: ニックネームでの匿名利用、招待コードでグループ参加
- 🍽️ **スマート推薦**: AIが会話内容を分析して好みを抽出
- 📊 **投票システム**: グループでの店舗選定
- 🔧 **REST API**: 完全なRESTful API設計

## 技術スタック

- **Framework**: FastAPI 0.104.1
- **Database**: SQLite (開発用) / PostgreSQL対応
- **AI**: OpenAI GPT-3.5-turbo
- **ORM**: SQLAlchemy 2.0.23
- **Validation**: Pydantic

## プロジェクト構造

```
/
├── main.py                 # アプリケーションエントリーポイント
├── requirements.txt        # Python依存関係
├── .env                   # 環境変数（OpenAI APIキー等）
├── Dockerfile             # Docker設定
├── docker-compose.yml     # Docker Compose設定
│
├── app/                   # メインアプリケーションパッケージ
│   ├── api/               # APIエンドポイント
│   │   ├── users.py       # ユーザー管理API
│   │   ├── groups.py      # グループ管理API
│   │   ├── hearings.py    # ヒアリング管理API
│   │   ├── interviews.py  # AIインタビュー機能
│   │   └── recommendations.py  # 推薦管理API
│   │
│   ├── core/              # 設定とユーティリティ
│   │   └── config.py      # アプリケーション設定
│   │
│   ├── db/                # データベース関連
│   │   └── database.py    # データベース接続とセッション管理
│   │
│   ├── models/            # SQLAlchemyモデル
│   │   ├── user.py        # ユーザーモデル
│   │   ├── group.py       # グループモデル
│   │   ├── hearing.py     # ヒアリングモデル
│   │   ├── interview.py   # インタビュー・メッセージモデル
│   │   └── recommendation.py  # 推薦・投票モデル
│   │
│   ├── schemas/           # Pydanticスキーマ
│   │   ├── user.py        # ユーザースキーマ
│   │   ├── group.py       # グループスキーマ
│   │   ├── hearing.py     # ヒアリングスキーマ
│   │   ├── interview.py   # インタビュースキーマ
│   │   └── recommendation.py  # 推薦スキーマ
│   │
│   └── clients/           # 外部サービスクライアント
│       └── openai_client.py  # OpenAI API連携
│
└── docs/                  # ドキュメント
    ├── Restaurant Recommendation API.md
    └── todo.md
```

## 環境設定

### 1. 環境変数ファイル（.env）の作成
```env
# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key_here

# データベース設定
DATABASE_URL=sqlite:///./restaurant_recommendation.db

# API設定
PROJECT_NAME=Restaurant Recommendation API
BACKEND_CORS_ORIGINS=["*"]
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. アプリケーションの起動
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

アプリケーションは `http://localhost:8000` で起動します。

### 4. API ドキュメント
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🚀 AIヒアリング機能の使い方

### 1. 新しいインタビューを開始
```bash
POST /api/interviews/
{
  "user_id": "user_uuid",
  "group_id": "group_uuid" // オプション
}
```

### 2. AIとチャット
```bash
POST /api/interviews/{interview_id}/chat
{
  "message": "予算は3000円くらいで、和食が好きです"
}
```

### 3. インタビュー完了
```bash
POST /api/interviews/{interview_id}/complete
```

## 利用可能なAPIエンドポイント

### ユーザー管理
- `POST /api/users/anonymous` - 匿名ユーザー作成
- `GET /api/users/{user_id}` - ユーザー情報取得
- `PUT /api/users/{user_id}` - ユーザー情報更新
- `DELETE /api/users/{user_id}` - ユーザー削除

### グループ管理
- `POST /api/groups` - 新しいグループ作成
- `POST /api/groups/join` - 招待コードでグループに参加
- `GET /api/groups/{group_id}` - グループ情報の取得
- `PUT /api/groups/{group_id}` - グループ情報更新

### AIインタビュー機能
- `POST /api/interviews/` - 新しいインタビューを開始
- `POST /api/interviews/{interview_id}/chat` - AIとチャット
- `POST /api/interviews/{interview_id}/complete` - インタビュー完了・分析
- `GET /api/interviews/{interview_id}` - インタビュー情報取得

### 推薦管理
- `POST /api/recommendations/` - 推薦作成
- `GET /api/recommendations/{recommendation_id}` - 推薦情報取得
- `POST /api/recommendations/{recommendation_id}/vote` - 店舗に投票
- `GET /api/recommendations/{recommendation_id}/results` - 投票結果取得

## 実装済み機能

### ✅ 完全実装済み
1. **AIヒアリング機能**
   - OpenAI GPT-3.5-turboによる自然な対話
   - 会話履歴の保存
   - 好み分析機能

2. **ユーザー・グループ管理**
   - 匿名ユーザー作成（ニックネーム）
   - 招待コードでのグループ参加
   - グループメンバー管理

3. **推薦・投票システム**
   - 店舗候補の生成
   - グループ内投票
   - 投票結果の集計

### 🔧 設定済み・準備完了
- Docker環境（Dockerfile、docker-compose.yml）
- 外部API連携準備（ぐるなび、Google Places）
- PostgreSQL対応準備
- 本格的なOpenAI API連携

## 動作確認手順

1. **サーバー起動**
   ```bash
   uvicorn main:app --reload
   ```

2. **Swagger UIアクセス**
   `http://localhost:8000/docs`

3. **基本フロー**
   - 匿名ユーザー作成 → グループ作成 → AIインタビュー → 推薦生成 → 投票

## Docker使用方法

```bash
# Docker Composeで起動
docker-compose up --build

# または個別にビルド・実行
docker build -t restaurant-api .
docker run -p 8000:8000 restaurant-api
```

## 開発・テスト

### 基本動作テスト
```bash
# アプリケーション起動
python main.py

# 別ターミナルでAPIテスト
curl -X POST "http://localhost:8000/api/users/anonymous" \
  -H "Content-Type: application/json" \
  -d '{"nickname": "テストユーザー"}'
```

この整理により、プロジェクトが正常に動作し、今後の機能拡張が容易になりました。
