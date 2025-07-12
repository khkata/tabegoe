from ..core.config import settings
from typing import List, Dict, Optional
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        # OpenAI APIキーが設定されている場合のみクライアントを初期化
        if self.api_key and self.api_key.startswith('sk-'):
            try:
                import openai
                # シンプルな初期化
                openai.api_key = self.api_key
                self.client = openai
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.warning("OpenAI library not installed. Using mock responses.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        OpenAI APIを使用してチャット補完を行う
        
        Args:
            messages: チャット履歴のリスト
            
        Returns:
            AIの応答メッセージ
        """
        if not self.client:
            # APIキーが設定されていない場合はモックレスポンスを返す
            return self._get_mock_response(messages)
        
        try:
            # 新しいOpenAI API v1.0+ 呼び出し方式
            import openai
            
            # 同期的にAPIを呼び出してからawaitで待機
            import asyncio
            
            def sync_api_call():
                try:
                    # OpenAI の新しいクライアント方式
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
                    raise e
            
            # 非同期実行
            response_content = await asyncio.get_event_loop().run_in_executor(
                None, sync_api_call
            )
            
            return response_content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # エラーが発生した場合はモックレスポンスを返す
            return self._get_mock_response(messages)
    
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
        
        # キーワードベースの応答
        content_lower = last_message.lower()
        
        # 予算関連
        if any(word in content_lower for word in ["予算", "お金", "値段", "価格", "円"]):
            if any(word in content_lower for word in ["1000", "千円", "安い", "リーズナブル"]):
                return "1000-2000円のリーズナブルな価格帯ですね！学生さんや気軽なランチにぴったりです。\n\n次に、どのような料理がお好みですか？和食、洋食、中華など、ジャンルを教えてください。"
            elif any(word in content_lower for word in ["5000", "高級", "記念日", "デート"]):
                return "5000円以上の高級レストランですね！特別な日のお食事にふさわしいお店を探しましょう。\n\n記念日やデートなど、どのような用途でしょうか？雰囲気も重視してご提案します。"
            else:
                return "予算について教えてくださりありがとうございます！\n\n続いて、お好みの料理ジャンルはありますか？例えば：\n• 和食（寿司、懐石、居酒屋）\n• 洋食（フレンチ、イタリアン、ステーキ）\n• アジア料理（中華、韓国、タイ料理）"
        
        # 料理ジャンル関連
        elif any(word in content_lower for word in ["和食", "寿司", "天ぷら", "懐石", "居酒屋"]):
            return "和食がお好みですね！日本料理の奥深い味わいを楽しめるお店を探しましょう。\n\n和食の中でも、寿司、天ぷら、懐石料理、居酒屋など、どのようなスタイルがお好みですか？\n\nまた、どちらのエリアをご希望でしょうか？"
        elif any(word in content_lower for word in ["イタリアン", "パスタ", "ピザ"]):
            return "イタリアンですね！パスタやピザの本格的な味を楽しめるお店を見つけましょう。\n\nカジュアルなトラットリアから本格的なリストランテまで、どのような雰囲気がお好みですか？\n\nエリアの希望もあれば教えてください。"
        elif any(word in content_lower for word in ["フレンチ", "フランス料理"]):
            return "フレンチですね！洗練されたフランス料理を楽しめるお店を探しましょう。\n\nカジュアルなビストロスタイル、または本格的なフランス料理店、どちらがお好みでしょうか？\n\n特別な日のお食事でしょうか？"
        elif any(word in content_lower for word in ["中華", "中国料理", "北京ダック", "麻婆豆腐"]):
            return "中華料理ですね！本格的な中国の味を堪能できるお店を見つけましょう。\n\n四川料理の辛さ、広東料理の繊細さ、北京料理の豪快さなど、どのような系統がお好みですか？\n\n辛いものは大丈夫でしょうか？"
        
        # 場所・エリア関連
        elif any(word in content_lower for word in ["渋谷", "新宿", "銀座", "恵比寿", "表参道", "六本木"]):
            locations = ["渋谷", "新宿", "銀座", "恵比寿", "表参道", "六本木"]
            mentioned_location = next((loc for loc in locations if loc in content_lower), "そちらのエリア")
            return f"{mentioned_location}エリアですね！アクセスも良く、たくさんの素敵なお店があります。\n\n駅からの距離はどの程度まで大丈夫でしょうか？\n• 駅直結・徒歩2分以内\n• 徒歩5分程度\n• 徒歩10分程度まで"
        elif any(word in content_lower for word in ["駅", "近く", "アクセス", "場所"]):
            return "アクセスについても重要ですね！\n\n最寄り駅や具体的なエリア名を教えていただけますか？\n\n例）渋谷駅周辺、新宿東口、銀座一丁目など\n\n駅からの距離の希望もあれば一緒にお聞かせください。"
        
        # アレルギー・制約関連  
        elif any(word in content_lower for word in ["アレルギー", "苦手", "食べられない", "ダメ"]):
            return "食べ物の制約について教えてくださりありがとうございます。安心してお食事を楽しんでいただくために大切な情報です。\n\n他にも何かアレルギーや苦手な食材があれば、遠慮なく教えてください。\n\n逆に、特に好きな食材や料理はありますか？"
        
        # 雰囲気・用途関連
        elif any(word in content_lower for word in ["デート", "記念日", "誕生日", "カップル"]):
            return "素敵な記念日のお食事ですね！💕\n\n特別な日にふさわしい、ロマンチックで上質な雰囲気のお店をご提案します。\n\n個室やカップルシート、夜景が見える席など、特別なご希望はありますか？"
        elif any(word in content_lower for word in ["友達", "仲間", "グループ", "会社"]):
            return "お友達やグループでのお食事ですね！\n\nみんなでワイワイ楽しめる雰囲気のお店を探しましょう。\n\n何名くらいでのご利用でしょうか？個室希望や、お酒を飲まれるかなども教えてください。"
        elif any(word in content_lower for word in ["家族", "両親", "子供", "ファミリー"]):
            return "ご家族でのお食事ですね！\n\nお子様連れでも安心してご利用いただけるお店をご提案します。\n\nお子様の年齢や、子供向けメニューの有無、座敷席の希望などがあれば教えてください。"
        
        # 一般的な応答
        else:
            remaining_questions = []
            user_messages = [m["content"] for m in messages if m["role"] == "user"]
            all_content = " ".join(user_messages).lower()
            
            if not any(word in all_content for word in ["予算", "円", "お金"]):
                remaining_questions.append("• ご予算（1000-2000円、3000-5000円など）")
            if not any(word in all_content for word in ["和食", "洋食", "中華", "イタリアン", "フレンチ"]):
                remaining_questions.append("• お好みの料理ジャンル")
            if not any(word in all_content for word in ["駅", "渋谷", "新宿", "銀座", "エリア"]):
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
