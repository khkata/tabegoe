# Restaurant Recommendation API

## 概要

気遣い合う少人数グループ（2〜6人）が外食先を決定する際、AIが個別に希望や制約を聞き出し、全員にとって最適な飲食店を推薦するサービスのバックエンドAPIです。ユーザーには匿名性があり、本音を話しやすくする設計になっています。

## 主な機能

- **ユーザー管理**: 匿名ユーザーの作成・管理
- **グループ管理**: 少人数グループの作成・メンバー管理
- **ヒアリング機能**: AIによる個別の希望・制約の聞き取り
- **推薦機能**: 全員の希望を考慮した飲食店の推薦

## 技術スタック

- **フレームワーク**: FastAPI 0.104.1
- **データベース**: SQLite（開発用）/ PostgreSQL（本番用対応）
- **ORM**: SQLAlchemy 2.0.23
- **バリデーション**: Pydantic 2.5.0
- **認証**: python-jose（JWT対応）
- **パスワードハッシュ**: passlib（bcrypt）

## ドメインモデル

### 1. User（ユーザー）
- 匿名性を保ちつつ、個人の好みや制約を管理
- 属性: user_id, preferences, created_at, updated_at

### 2. Group（グループ）
- 外食先を決定する少人数の集まり（2〜6人）
- 属性: group_id, name, status, created_at, updated_at
- ステータス: active, completed, cancelled

### 3. Hearing（ヒアリング）
- AIがユーザーから個別に希望や制約を聞き出すプロセス
- 属性: hearing_id, group_id, user_id, question, answer, status, created_at, updated_at
- ステータス: pending, completed, skipped

### 4. Recommendation（推薦）
- ヒアリング結果に基づく飲食店の推薦結果
- 属性: recommendation_id, group_id, recommended_restaurants, reasoning, created_at

## API エンドポイント

### ユーザー管理
- `POST /api/v1/users/` - ユーザー作成
- `GET /api/v1/users/{user_id}` - ユーザー情報取得
- `PUT /api/v1/users/{user_id}` - ユーザー情報更新
- `DELETE /api/v1/users/{user_id}` - ユーザー削除

### グループ管理
- `POST /api/v1/groups/` - グループ作成
- `GET /api/v1/groups/{group_id}` - グループ情報取得
- `PUT /api/v1/groups/{group_id}` - グループ情報更新
- `POST /api/v1/groups/{group_id}/members/{user_id}` - メンバー追加
- `DELETE /api/v1/groups/{group_id}/members/{user_id}` - メンバー削除

### ヒアリング管理
- `POST /api/v1/hearings/` - ヒアリング作成
- `GET /api/v1/hearings/{hearing_id}` - ヒアリング情報取得
- `PUT /api/v1/hearings/{hearing_id}` - ヒアリング情報更新（回答追加）
- `GET /api/v1/hearings/group/{group_id}` - グループのヒアリング一覧
- `GET /api/v1/hearings/user/{user_id}` - ユーザーのヒアリング一覧
- `GET /api/v1/hearings/group/{group_id}/user/{user_id}` - 特定グループ・ユーザーのヒアリング

### 推薦管理
- `POST /api/v1/recommendations/` - 推薦作成
- `GET /api/v1/recommendations/{recommendation_id}` - 推薦情報取得
- `GET /api/v1/recommendations/group/{group_id}` - グループの推薦一覧

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. アプリケーションの起動
```bash
python main.py
```

アプリケーションは `http://localhost:8000` で起動します。

### 3. API ドキュメント
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`

## 使用例

### ユーザー作成
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"preferences": "{\"cuisine\": \"Japanese\", \"budget\": \"medium\"}"}'
```

### グループ作成
```bash
curl -X POST "http://localhost:8000/api/v1/groups/" \
  -H "Content-Type: application/json" \
  -d '{"name": "同僚ランチ", "member_ids": ["user-id-1", "user-id-2"]}'
```

### ヒアリング作成
```bash
curl -X POST "http://localhost:8000/api/v1/hearings/" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": "group-id",
    "user_id": "user-id",
    "question": "どのような料理がお好みですか？"
  }'
```

## データベース設計

SQLiteを使用した開発環境向けの設計ですが、PostgreSQLにも対応可能です。主要なテーブル：

- `users` - ユーザー情報
- `groups` - グループ情報
- `group_members` - グループとユーザーの関連（多対多）
- `hearings` - ヒアリング情報
- `recommendations` - 推薦情報

## 今後の拡張予定

1. **AI統合**: 実際のAIサービスとの連携によるヒアリング自動化
2. **外部API連携**: 飲食店情報取得のための外部サービス連携
3. **認証・認可**: JWT認証の実装
4. **リアルタイム通信**: WebSocketによるリアルタイム更新
5. **推薦アルゴリズム**: より高度な推薦ロジックの実装

## ライセンス

MIT License

