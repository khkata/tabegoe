import requests
import logging
from typing import Dict, List, Optional, Any
from ..core.config import settings

logger = logging.getLogger(__name__)

class HotPepperClient:
    """ホットペッパーグルメAPIクライアント"""
    
    def __init__(self):
        self.base_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        self.api_key = settings.HOTPEPPER_API_KEY
        
    def search_restaurants(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """レストラン検索"""
        try:
            # APIキーと基本パラメータを設定
            search_params = {
                'key': self.api_key,
                'format': 'json',
                'count': 20,  # 最大20件取得
                'order': 4,   # おすすめ順
                **params
            }
            
            # 空の値を除去
            search_params = {k: v for k, v in search_params.items() if v is not None and v != ''}
            
            logger.info(f"HotPepper API search with params: {search_params}")
            
            response = requests.get(self.base_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data and 'shop' in data['results']:
                return data
            else:
                logger.warning(f"No results found in HotPepper API response: {data}")
                return {'results': {'shop': []}}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"HotPepper API request failed: {e}")
            raise Exception(f"レストラン検索でエラーが発生しました: {str(e)}")
        except Exception as e:
            logger.error(f"HotPepper API error: {e}")
            raise Exception(f"APIエラー: {str(e)}")
    
    def merge_user_preferences(self, user_preferences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """複数ユーザーの希望条件をマージして検索クエリを生成"""
        if not user_preferences:
            return {}
        
        merged_params = {}
        
        # 場所のマージ（緯度経度の中心点計算）
        locations = []
        for prefs in user_preferences:
            if prefs.get('lat') and prefs.get('lng'):
                locations.append({
                    'lat': float(prefs['lat']),
                    'lng': float(prefs['lng']),
                    'range': prefs.get('range', 3)
                })
        
        if locations:
            # 中心点を計算
            avg_lat = sum(loc['lat'] for loc in locations) / len(locations)
            avg_lng = sum(loc['lng'] for loc in locations) / len(locations)
            max_range = max(loc['range'] for loc in locations)
            
            merged_params.update({
                'lat': avg_lat,
                'lng': avg_lng,
                'range': max_range
            })
        
        # キーワードのマージ
        keywords = []
        for prefs in user_preferences:
            if prefs.get('keyword'):
                keywords.extend(prefs['keyword'].split())
        
        if keywords:
            # 重複を除去してスペース区切りで結合
            unique_keywords = list(set(keywords))
            merged_params['keyword'] = ' '.join(unique_keywords)
        
        # ジャンルのマージ（複数指定可能）
        genres = []
        for prefs in user_preferences:
            if prefs.get('genre'):
                if isinstance(prefs['genre'], list):
                    genres.extend(prefs['genre'])
                else:
                    genres.append(prefs['genre'])
        
        if genres:
            # 重複を除去
            unique_genres = list(set(genres))
            merged_params['genre'] = ','.join(unique_genres)
        
        # 予算のマージ（最も包括的な範囲）
        budgets = []
        for prefs in user_preferences:
            if prefs.get('budget'):
                if isinstance(prefs['budget'], list):
                    budgets.extend(prefs['budget'])
                else:
                    budgets.append(prefs['budget'])
        
        if budgets:
            unique_budgets = list(set(budgets))
            merged_params['budget'] = ','.join(unique_budgets[:2])  # 最大2個まで
        
        # 人数のマージ（最大人数を採用）
        party_capacities = []
        for prefs in user_preferences:
            if prefs.get('party_capacity'):
                party_capacities.append(int(prefs['party_capacity']))
        
        if party_capacities:
            merged_params['party_capacity'] = max(party_capacities)
        
        # その他の条件（AND条件でマージ）
        boolean_fields = [
            'wifi', 'wedding', 'course', 'free_drink', 'free_food',
            'private_room', 'horigotatsu', 'tatami', 'cocktail', 'shochu',
            'sake', 'wine', 'card', 'non_smoking', 'charter', 'ktai',
            'parking', 'barrier_free', 'sommelier', 'night_view', 'open_air',
            'show', 'equipment', 'karaoke', 'band', 'tv', 'lunch',
            'midnight', 'midnight_meal', 'english', 'pet', 'child'
        ]
        
        for field in boolean_fields:
            # 全員が希望している場合のみ条件に追加
            field_values = []
            for prefs in user_preferences:
                if field in prefs:
                    field_values.append(prefs[field])
            
            if field_values and all(v == 1 for v in field_values):
                merged_params[field] = 1
        
        logger.info(f"Merged search parameters: {merged_params}")
        return merged_params
    
    def convert_to_restaurant_data(self, shop_data: Dict[str, Any]) -> Dict[str, Any]:
        """ホットペッパーAPIのレスポンスを内部のレストランデータ形式に変換"""
        return {
            'restaurant_id': shop_data.get('id', ''),
            'name': shop_data.get('name', ''),
            'cuisine_type': shop_data.get('genre', {}).get('name', ''),
            'address': shop_data.get('address', ''),
            'price_range': shop_data.get('budget', {}).get('name', ''),
            'external_rating': 4.0,  # ホットペッパーAPIには評価がないのでデフォルト値
            'external_review_count': 100,  # デフォルト値
            'image_url': self._get_image_url(shop_data),
            'description': shop_data.get('catch', ''),
            'access': shop_data.get('access', ''),
            'capacity': shop_data.get('capacity', ''),
            'open_hours': shop_data.get('open', ''),
            'closed_days': shop_data.get('close', ''),
            'lat': shop_data.get('lat', 0),
            'lng': shop_data.get('lng', 0),
            'url': shop_data.get('urls', {}).get('pc', ''),
            'features': self._extract_features(shop_data)
        }
    
    def _get_image_url(self, shop_data: Dict[str, Any]) -> str:
        """レストランの画像URLを取得"""
        photo = shop_data.get('photo', {})
        if photo.get('pc', {}).get('l'):
            return photo['pc']['l']
        elif photo.get('pc', {}).get('m'):
            return photo['pc']['m']
        elif photo.get('pc', {}).get('s'):
            return photo['pc']['s']
        return ''
    
    def _extract_features(self, shop_data: Dict[str, Any]) -> List[str]:
        """レストランの特徴を抽出"""
        features = []
        
        feature_mapping = {
            'wifi': 'WiFi完備',
            'private_room': '個室あり',
            'free_drink': '飲み放題',
            'free_food': '食べ放題',
            'card': 'カード可',
            'non_smoking': '禁煙席',
            'parking': '駐車場あり',
            'night_view': '夜景がキレイ',
            'course': 'コースあり',
            'karaoke': 'カラオケ',
            'child': 'お子様連れOK'
        }
        
        for key, label in feature_mapping.items():
            if shop_data.get(key) == 'あり' or shop_data.get(key) == '1':
                features.append(label)
        
        return features

hotpepper_client = HotPepperClient()
