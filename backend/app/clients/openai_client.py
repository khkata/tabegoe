from ..core.config import settings
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class ChatResponse:
    """チャット応答のレスポンス"""
    content: str
    is_mock: bool
    source: str  # "openai" or "mock"
    model: Optional[str] = None


class OpenAIClient:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        # OpenAI APIキーが設定されている場合のみクライアントを初期化
        if self.api_key and self.api_key.startswith('sk-'):
            try:
                import openai
                # v1.0+では直接クライアントを作成（初期化時にはテスト呼び出ししない）
                self.client = True  # クライアントが利用可能であることを示すフラグ
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.warning("OpenAI library not installed. Using mock responses.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> ChatResponse:
        """
        OpenAI APIを使用してチャット補完を行う
        
        Args:
            messages: チャット履歴のリスト
            
        Returns:
            ChatResponse: 応答内容とメタデータ
        """
        if not self.client:
            # APIキーが設定されていない場合はモックレスポンスを返す
            mock_content = self._get_mock_response(messages)
            return ChatResponse(
                content=mock_content,
                is_mock=True,
                source="mock",
                model=None
            )
        
        try:
            # 新しいOpenAI API v1.0+ 呼び出し方式
            import openai
            
            # 同期的にAPIを呼び出してからawaitで待機
            import asyncio
            
            def sync_api_call():
                try:
                    # より簡単な初期化方式を試す
                    import openai
                    client = openai.OpenAI(api_key=self.api_key)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    logger.error(f"OpenAI API sync call error: {e}")
                    # より詳細なエラー情報をログに記録
                    import traceback
                    logger.error(traceback.format_exc())
                    raise e
            
            # 非同期実行
            response_content = await asyncio.get_event_loop().run_in_executor(
                None, sync_api_call
            )
            
            return ChatResponse(
                content=response_content,
                is_mock=False,
                source="openai",
                model="gpt-3.5-turbo"
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # エラーが発生した場合はモックレスポンスを返す
            mock_content = self._get_mock_response(messages)
            return ChatResponse(
                content=mock_content,
                is_mock=True,
                source="mock",
                model=None
            )
    
    def _get_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """モックレスポンス（開発・テスト用）"""
        last_message = messages[-1]["content"] if messages else ""
        message_count = len([m for m in messages if m["role"] == "user"])
        
        # 最初のメッセージかチェック
        if message_count <= 1:
            return """こんにちは！レストラン選びのお手伝いをさせていただきます。

まず、以下について教えてください：

1️⃣ **ご予算の目安**
   ランチ：1000-2000円 / ディナー：3000-5000円など

2️⃣ **お好みの料理ジャンル**
   和食、洋食、中華、イタリアン、フレンチなど

3️⃣ **希望するエリア**
   最寄り駅や地域名

何から聞かせていただきましょうか？"""
        
        # 全てのユーザーメッセージを結合して文脈を把握
        user_messages = [m["content"] for m in messages if m["role"] == "user"]
        all_user_content = " ".join(user_messages).lower()
        current_message = last_message.lower()
        
        # 既に得られている情報をチェック
        has_budget = any(word in all_user_content for word in ["予算", "円", "お金", "1000", "2000", "3000", "5000", "安い", "高い", "リーズナブル", "ランチ", "ディナー"])
        has_cuisine = any(word in all_user_content for word in ["和食", "寿司", "天ぷら", "懐石", "居酒屋", "イタリアン", "パスタ", "ピザ", "フレンチ", "中華", "中国料理", "韓国", "タイ"])
        has_location = any(word in all_user_content for word in ["駅", "渋谷", "新宿", "銀座", "エリア", "大阪", "東京", "名古屋", "京都", "神戸", "福岡", "梅田", "心斎橋", "難波", "天王寺"])
        
        # 情報が揃っているかチェック
        if has_budget and has_cuisine and has_location:
            # 特別要望が既に含まれているかチェック
            has_special_request = any(word in all_user_content for word in ["個室", "禁煙", "子供", "ベジタリアン", "特になし", "なし"])
            if has_special_request:
                return "ありがとうございます！すべての情報が揃いました。\n\n条件：\n• 予算：2000円程度\n• 料理：寿司・海鮮\n• エリア：大阪\n• その他：個室希望\n\nこれらの条件でお店を探しています。ヒアリングを完了いたします。"
            else:
                return "素晴らしい！ご希望の条件が揃いましたね。\n\n最後に、特別なご要望はありますか？\n• 個室希望\n• 禁煙席\n• 子供連れ歓迎\n• ベジタリアン対応\n\n特になければ「特になし」とお答えください。これでレストランをお探しします！"
        
        # 現在のメッセージで新しい情報が追加されたかチェック
        message_adds_budget = any(word in current_message for word in ["予算", "円", "お金", "1000", "2000", "3000", "5000", "安い", "高い", "リーズナブル"])
        message_adds_cuisine = any(word in current_message for word in ["和食", "寿司", "天ぷら", "懐石", "居酒屋", "イタリアン", "パスタ", "ピザ", "フレンチ", "中華", "中国料理", "韓国", "タイ"])
        message_adds_location = any(word in current_message for word in ["渋谷", "新宿", "銀座", "大阪", "東京", "名古屋", "京都", "神戸", "福岡", "梅田", "心斎橋", "難波", "天王寺"])
        
        # 予算が追加された場合
        if message_adds_budget and not has_budget:
            if any(word in current_message for word in ["1000", "千円", "安い", "リーズナブル"]):
                response = "1000-2000円のリーズナブルな価格帯ですね！学生さんや気軽なランチにぴったりです。"
            elif any(word in current_message for word in ["5000", "高級", "記念日", "デート"]):
                response = "5000円以上の高級レストランですね！特別な日のお食事にふさわしいお店を探しましょう。"
            else:
                response = "予算について教えてくださりありがとうございます！"
            
            # 次に必要な情報を聞く
            if not has_cuisine:
                response += "\n\n次に、どのような料理がお好みですか？\n• 和食（寿司、懐石、居酒屋）\n• 洋食（フレンチ、イタリアン、ステーキ）\n• アジア料理（中華、韓国、タイ料理）"
            elif not has_location:
                response += "\n\nどちらのエリアをご希望でしょうか？最寄り駅や地域名を教えてください。"
            return response
        
        # 料理ジャンルが追加された場合
        if message_adds_cuisine and not has_cuisine:
            if any(word in current_message for word in ["和食", "寿司", "天ぷら", "懐石", "居酒屋"]):
                response = "和食がお好みですね！日本料理の奥深い味わいを楽しめるお店を探しましょう。"
            elif any(word in current_message for word in ["イタリアン", "パスタ", "ピザ"]):
                response = "イタリアンですね！パスタやピザの本格的な味を楽しめるお店を見つけましょう。"
            elif any(word in current_message for word in ["フレンチ", "フランス料理"]):
                response = "フレンチですね！洗練されたフランス料理を楽しめるお店を探しましょう。"
            elif any(word in current_message for word in ["中華", "中国料理", "北京ダック", "麻婆豆腐"]):
                response = "中華料理ですね！本格的な中国の味を堪能できるお店を見つけましょう。"
            else:
                response = "料理ジャンルありがとうございます！"
            
            # 次に必要な情報を聞く
            if not has_budget:
                response += "\n\nご予算の目安を教えてください。\n• ランチ：1000-2000円\n• ディナー：3000-5000円\n• 高級：5000円以上"
            elif not has_location:
                response += "\n\nどちらのエリアをご希望でしょうか？最寄り駅や地域名を教えてください。"
            return response
        
        # エリアが追加された場合
        if message_adds_location and not has_location:
            locations = ["渋谷", "新宿", "銀座", "恵比寿", "表参道", "六本木", "大阪", "東京", "名古屋", "京都", "神戸", "福岡", "梅田", "心斎橋", "難波", "天王寺"]
            mentioned_location = next((loc for loc in locations if loc in current_message), "そちらのエリア")
            response = f"{mentioned_location}エリアですね！アクセスも良く、たくさんの素敵なお店があります。"
            
            # 次に必要な情報を聞く
            if not has_budget:
                response += "\n\nご予算の目安を教えてください。\n• ランチ：1000-2000円\n• ディナー：3000-5000円\n• 高級：5000円以上"
            elif not has_cuisine:
                response += "\n\nどのような料理がお好みですか？\n• 和食（寿司、懐石、居酒屋）\n• 洋食（フレンチ、イタリアン、ステーキ）\n• アジア料理（中華、韓国、タイ料理）"
            return response
        
        # 特殊なケース：複数の情報が一度に提供された場合
        if "寿司" in current_message and "大阪" in current_message:
            response = "和食（寿司）で大阪エリアですね！素晴らしい選択です。大阪は美味しい寿司店がたくさんありますね。"
            if not has_budget:
                response += "\n\nご予算の目安を教えてください。\n• ランチ：1000-2000円\n• ディナー：3000-5000円\n• 高級：5000円以上"
            return response
        
        # デフォルト：まだ足りない情報を聞く
        remaining_questions = []
        if not has_budget:
            remaining_questions.append("• ご予算（1000-2000円、3000-5000円など）")
        if not has_cuisine:
            remaining_questions.append("• お好みの料理ジャンル")
        if not has_location:
            remaining_questions.append("• 希望するエリア・最寄り駅")
        
        if remaining_questions:
            return f"ありがとうございます！\n\n他にも以下について教えていただけると、より良いお店をご提案できます：\n\n{chr(10).join(remaining_questions)}\n\n何でもお気軽にお聞かせください！"
        else:
            return "詳しく教えてくださりありがとうございます！\n\n最後に、特別なご要望（個室希望、禁煙席、ベジタリアン対応など）があれば教えてください。\n\nなければ「特になし」と言っていただければ、ヒアリングを完了します。"
    
    async def analyze_preferences(self, messages: List[Dict[str, str]]) -> Dict:
        """
        インタビューメッセージから好みを分析
        
        Args:
            messages: インタビューのメッセージ履歴
            
        Returns:
            分析された好みの辞書
        """
        if not self.client:
            return self._get_mock_preferences(messages)
        
        try:
            # 実際のOpenAI API呼び出し
            analysis_prompt = """
以下のインタビューから、ユーザーのレストランの好みを分析してJSON形式で返してください。
分析内容:
- budget: 予算（例: "1000-2000", "3000-5000"）
- cuisine_types: 好みの料理ジャンル（リスト）
- location: 希望エリア
- allergies: アレルギー・苦手な食材（リスト）
- atmosphere: 雰囲気の好み
- special_requests: その他の要望

インタビュー内容:
""" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            if hasattr(self.client, 'chat'):
                # 非同期クライアント
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": analysis_prompt}],
                        max_tokens=300,
                        temperature=0.3
                    )
                )
            else:
                # 同期クライアントをasyncioで包む
                import asyncio
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": analysis_prompt}],
                        max_tokens=300,
                        temperature=0.3
                    )
                )
            
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return self._get_mock_preferences(messages)
                
        except Exception as e:
            logger.error(f"OpenAI preference analysis error: {e}")
            return self._get_mock_preferences(messages)
    
    def _get_mock_preferences(self, messages: List[Dict[str, str]]) -> Dict:
        """モック好み分析（開発・テスト用）"""
        user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
        content = " ".join(user_messages).lower()
        
        preferences = {
            "budget": "2000-4000",
            "cuisine_types": [],
            "location": "",
            "allergies": [],
            "atmosphere": "カジュアル",
            "special_requests": []
        }
        
        # 予算の詳細分析
        if any(word in content for word in ["1000", "千円", "安い", "リーズナブル", "学生"]):
            preferences["budget"] = "1000-2000"
        elif any(word in content for word in ["5000", "高級", "記念日", "デート", "特別"]):
            preferences["budget"] = "4000-8000"
        elif any(word in content for word in ["3000", "普通", "標準"]):
            preferences["budget"] = "2500-4000"
        elif any(word in content for word in ["2000", "ランチ"]):
            preferences["budget"] = "1500-3000"
        
        # 料理ジャンルの詳細分析
        cuisine_mapping = {
            "和食": ["和食", "寿司", "天ぷら", "懐石", "居酒屋", "刺身", "日本料理"],
            "イタリアン": ["イタリアン", "パスタ", "ピザ", "イタリア"],
            "フレンチ": ["フレンチ", "フランス料理", "フランス", "ビストロ"],
            "中華": ["中華", "中国料理", "中国", "北京ダック", "麻婆豆腐", "餃子"],
            "韓国料理": ["韓国", "キムチ", "サムギョプサル", "ビビンバ"],
            "タイ料理": ["タイ", "トムヤムクン", "パッタイ"],
            "洋食": ["洋食", "ステーキ", "ハンバーグ"],
            "焼肉": ["焼肉", "カルビ", "ホルモン"]
        }
        
        for cuisine, keywords in cuisine_mapping.items():
            if any(keyword in content for keyword in keywords):
                preferences["cuisine_types"].append(cuisine)
        
        # 場所の分析
        locations = ["渋谷", "新宿", "銀座", "恵比寿", "表参道", "六本木", "池袋", "上野", "浅草", "秋葉原"]
        for location in locations:
            if location in content:
                preferences["location"] = location
                break
        
        # アレルギー分析
        allergy_keywords = {
            "魚介類": ["魚", "エビ", "カニ", "貝", "魚介", "海老", "蟹"],
            "卵": ["卵", "たまご"],
            "乳製品": ["牛乳", "チーズ", "乳製品", "ミルク"],
            "ナッツ": ["ナッツ", "ピーナッツ", "アーモンド"],
            "そば": ["そば", "蕎麦"],
            "辛い物": ["辛い", "スパイシー", "激辛", "唐辛子"]
        }
        
        for allergy, keywords in allergy_keywords.items():
            if any(f"{keyword}が苦手" in content or f"{keyword}はダメ" in content or f"{keyword}アレルギー" in content 
                   for keyword in keywords):
                preferences["allergies"].append(allergy)
        
        # 雰囲気の分析
        if any(word in content for word in ["デート", "記念日", "誕生日", "ロマンチック"]):
            preferences["atmosphere"] = "ロマンチック"
        elif any(word in content for word in ["会社", "接待", "ビジネス", "商談"]):
            preferences["atmosphere"] = "フォーマル"
        elif any(word in content for word in ["家族", "子供", "ファミリー"]):
            preferences["atmosphere"] = "ファミリー向け"
        elif any(word in content for word in ["友達", "仲間", "グループ", "ワイワイ"]):
            preferences["atmosphere"] = "カジュアル・グループ向け"
        elif any(word in content for word in ["静か", "落ち着い", "大人"]):
            preferences["atmosphere"] = "落ち着いた大人の空間"
        
        # 特別なリクエスト
        special_requests = []
        if any(word in content for word in ["個室", "プライベート"]):
            special_requests.append("個室希望")
        if any(word in content for word in ["禁煙", "タバコ"]):
            special_requests.append("禁煙席希望")
        if any(word in content for word in ["夜景", "景色", "眺め"]):
            special_requests.append("眺めの良い席希望")
        if any(word in content for word in ["駐車場", "車"]):
            special_requests.append("駐車場あり")
        if any(word in content for word in ["ベジタリアン", "野菜", "菜食"]):
            special_requests.append("ベジタリアン対応")
        if any(word in content for word in ["子供", "キッズ"]):
            special_requests.append("子供連れ歓迎")
        
        preferences["special_requests"] = special_requests
        
        return preferences


# グローバルインスタンス
openai_client = OpenAIClient()
