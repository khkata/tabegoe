# tabegoe - AIレストラン推薦システム

tabegoeは、グループでのレストラン選びを簡単にするAI搭載のWebアプリケーションです。各メンバーがAIヒアリングを受けて、全員の希望を考慮した最適なレストランを推薦・投票・決定できます。

## 🎯 主な機能

### グループ管理
- **グループ作成**: ホストがグループを作成し、招待コードで参加者を招待
- **匿名参加**: ユーザー登録不要で簡単に参加可能
- **リアルタイム同期**: メンバーの参加状況をリアルタイムで確認

### AIヒアリング
- **個別インタビュー**: 各メンバーがAIとチャットでヒアリング
- **好み分析**: 料理の種類、価格帯、雰囲気などを詳細に分析
- **完了追跡**: 全メンバーのヒアリング進捗を管理

### AI推薦システム
- **統合分析**: 全メンバーのヒアリング結果を統合
- **最適化推薦**: グループ全体に最適なレストランを複数提案
- **詳細情報**: 住所、評価、価格帯、推薦理由を表示

### 投票・決定システム
- **1人1票制**: 公平な投票システム
- **リアルタイム集計**: 投票状況をリアルタイムで表示
- **ホスト決定権**: 最終決定はホストが行う
- **自動遷移**: 決定後は全員が結果ページに自動遷移

## 🏗️ システム構成

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/        # 再利用可能なUIコンポーネント
│   │   ├── Layout/       # レイアウトコンポーネント
│   │   └── UI/           # ボタン、ローディングスピナーなど
│   ├── pages/            # 各画面のコンポーネント
│   │   ├── Landing.tsx       # ランディングページ
│   │   ├── UserCreate.tsx    # ユーザー作成
│   │   ├── GroupCreate.tsx   # グループ作成
│   │   ├── GroupJoin.tsx     # グループ参加
│   │   ├── GroupLobby.tsx    # グループロビー
│   │   ├── Interview.tsx     # AIヒアリング
│   │   ├── Recommendations.tsx # 推薦表示
│   │   ├── Vote.tsx          # 投票
│   │   └── Result.tsx        # 決定結果
│   ├── services/         # API通信
│   ├── store/           # 状態管理 (Zustand)
│   └── types/           # TypeScript型定義
├── package.json
└── vite.config.ts       # Vite設定
```

### Backend (FastAPI + Python)
```
backend/
├── app/
│   ├── api/             # APIエンドポイント
│   │   ├── groups.py        # グループ管理API
│   │   ├── users.py         # ユーザー管理API
│   │   ├── interviews.py    # ヒアリングAPI
│   │   ├── recommendations.py # 推薦・投票API
│   │   └── hearings.py      # 従来のヒアリング（廃止予定）
│   ├── clients/         # 外部API連携
│   │   └── openai_client.py # OpenAI GPT連携
│   ├── core/            # 設定・共通機能
│   │   ├── config.py        # 環境設定
│   │   └── external_api_client.py # 外部API設定
│   ├── db/              # データベース
│   │   └── database.py      # DB接続設定
│   ├── models/          # SQLAlchemyモデル
│   │   ├── user.py          # ユーザーモデル
│   │   ├── group.py         # グループモデル
│   │   ├── interview.py     # インタビューモデル
│   │   ├── recommendation.py # 推薦・投票モデル
│   │   └── hearing.py       # 従来モデル（廃止予定）
│   └── schemas/         # Pydantic スキーマ
│       ├── user.py          # ユーザースキーマ
│       ├── group.py         # グループスキーマ
│       ├── interview.py     # インタビュースキーマ
│       └── recommendation.py # 推薦スキーマ
├── docker-compose.yml   # Docker構成
├── Dockerfile          # Dockerイメージ定義
├── requirements.txt    # Python依存関係
└── main.py            # アプリケーションエントリーポイント
```

### Database (PostgreSQL)
```sql
-- 主要テーブル構成
users               -- ユーザー情報
groups              -- グループ情報
group_members       -- グループメンバー関係
interviews          -- AIヒアリング記録
recommendations     -- 推薦結果
restaurant_candidates -- 推薦レストラン候補
votes               -- 投票記録
```

## 🚀 セットアップ・起動方法

### 必要な環境
- Node.js 18+
- Docker & Docker Compose
- OpenAI API Key

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd tabegoe
```

### 2. Backend セットアップ
```bash
cd backend

# 環境変数ファイルを作成
cp .env.example .env

# .envファイルを編集してOpenAI API Keyを設定
# OPENAI_API_KEY=your_openai_api_key_here

# Dockerでバックエンドとデータベースを起動
docker-compose up -d

# ログを確認
docker logs backend-app-1
```

### 3. Frontend セットアップ
```bash
cd frontend

# 依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev
```

### 4. アクセス
- **Frontend**: http://localhost:5173 (または 5174)
- **Backend API**: http://localhost:8001
- **Database**: localhost:5432

## 📱 使用方法

### 1. グループの作成・参加
1. トップページで「グループを作成」または「グループに参加」を選択
2. ユーザー情報（ニックネーム）を入力
3. グループ名を設定（作成時）または招待コードを入力（参加時）

### 2. AIヒアリング
1. グループロビーで「ヒアリングを開始」をクリック
2. AIとチャットでレストランの好みをヒアリング
3. 料理の種類、価格帯、雰囲気などについて回答
4. 完了後、自動的にロビーに戻る

### 3. 推薦確認・投票
1. 全メンバーのヒアリング完了後、「🎯レストラン推薦を見る」ボタンが表示
2. AI分析による推薦レストラン一覧を確認
3. 気に入ったお店に投票（1人1票）
4. 投票後、自動的に投票結果ページに遷移

### 4. 最終決定
1. 全員の投票完了後、各レストランの得票数を表示
2. ホストが最終決定ボタンをクリック
3. 全メンバーが結果ページに自動遷移
4. 決定されたレストラン情報を確認

## 🔧 技術スタック

### Frontend
- **React 18**: UIライブラリ
- **TypeScript**: 型安全な開発
- **Vite**: 高速ビルドツール
- **Tailwind CSS**: スタイリング
- **Zustand**: 軽量状態管理
- **React Router**: ルーティング
- **React Hook Form**: フォーム管理
- **React Hot Toast**: 通知システム
- **Axios**: HTTP通信

### Backend
- **FastAPI**: 高性能WebAPIフレームワーク
- **SQLAlchemy**: ORM
- **PostgreSQL**: データベース
- **OpenAI GPT-4**: AI会話エンジン
- **Pydantic**: データバリデーション
- **Docker**: コンテナ化

### Infrastructure
- **Docker Compose**: 開発環境
- **PostgreSQL 14**: データベース
- **Uvicorn**: ASGIサーバー

## 🌟 主な特徴

### UX設計
- **エラーレス体験**: エラー時は自動的に適切なページにリダイレクト
- **リアルタイム同期**: メンバーの状況をリアルタイムで同期
- **ブラウザ更新対応**: ページ更新後も状態を復元
- **レスポンシブ対応**: モバイル・デスクトップ両対応

### データ設計
- **永続化**: Zustandによる状態の自動保存
- **関係性**: 正規化されたテーブル設計
- **一意性制約**: 重複投票防止機能
- **トランザクション**: データ整合性保証

### セキュリティ
- **CORS設定**: 適切なOrigin制限
- **バリデーション**: 入力データの検証
- **エラーハンドリング**: 適切なエラー処理

## 🛠️ 開発・デバッグ

### ログ確認
```bash
# バックエンドログ
docker logs backend-app-1 --tail 50

# データベース接続
docker exec -it backend-db-1 psql -U restaurant_user -d restaurant_recommendation
```

### データベース操作
```sql
-- テーブル構造確認
\d table_name

-- データ確認
SELECT * FROM groups;
SELECT * FROM interviews;
SELECT * FROM recommendations;
```

### フロントエンド開発
```bash
# 型チェック
npm run type-check

# ビルド
npm run build

# プレビュー
npm run preview
```

## 📚 API仕様

### 主要エンドポイント

#### グループ管理
- `POST /api/groups/` - グループ作成
- `POST /api/groups/join` - グループ参加
- `GET /api/groups/{group_id}` - グループ情報取得

#### ヒアリング
- `POST /api/interviews/groups/{group_id}/users/{user_id}/start` - ヒアリング開始
- `POST /api/interviews/{interview_id}/chat` - チャット送信
- `POST /api/interviews/{interview_id}/complete` - ヒアリング完了
- `GET /api/interviews/groups/{group_id}/status` - グループヒアリング状況

#### 推薦・投票
- `POST /api/recommendations/groups/{group_id}/recommendations` - 推薦生成
- `GET /api/recommendations/groups/{group_id}/recommendations` - 推薦取得
- `POST /api/recommendations/candidates/{candidate_id}/vote` - 投票
- `GET /api/recommendations/groups/{group_id}/votes` - 投票結果取得
- `POST /api/recommendations/groups/{group_id}/final-decision` - 最終決定
- `GET /api/recommendations/groups/{group_id}/final-decision` - 最終決定取得

## 🔄 今後の開発予定

### 機能拡張
- [ ] レストラン詳細情報の充実
- [ ] 地図連携機能
- [ ] 予約システム連携
- [ ] グループチャット機能
- [ ] 履歴・お気に入り機能

### 技術改善
- [ ] テストコード追加
- [ ] パフォーマンス最適化
- [ ] セキュリティ強化
- [ ] 多言語対応
- [ ] PWA対応

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します！

1. Forkしてください
2. Feature branchを作成してください (`git checkout -b feature/AmazingFeature`)
3. 変更をCommitしてください (`git commit -m 'Add some AmazingFeature'`)
4. Branchにプッシュしてください (`git push origin feature/AmazingFeature`)
5. Pull Requestを開いてください

## 📝 ライセンス

このプロジェクトは MIT License の下で公開されています。

## 📞 サポート

質問や問題がある場合は、Issueを作成してください。

---

**tabegoe** - AIが導く、みんなで決めるレストラン選び 🍽️✨
