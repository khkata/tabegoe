import requests
import json
from typing import List, Dict, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class GurunaviAPIClient:
    """ぐるなびAPI連携クライアント"""
    
    def __init__(self):
        self.base_url = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
        self.api_key = getattr(settings, 'GURUNAVI_API_KEY', None)
    
    def search_restaurants(
        self,
        latitude: float,
        longitude: float,
        range_km: int = 3,
        hit_per_page: int = 10,
        cuisine_type: Optional[str] = None,
        budget: Optional[str] = None
    ) -> List[Dict]:
        """
        レストラン検索
        
        Args:
            latitude: 緯度
            longitude: 経度
            range_km: 検索範囲（km）
            hit_per_page: 取得件数
            cuisine_type: 料理ジャンル
            budget: 予算
        
        Returns:
            レストラン情報のリスト
        """
        if not self.api_key:
            logger.warning("Gurunavi API key not configured, returning mock data")
            return self._get_mock_restaurants()
        
        params = {
            'keyid': self.api_key,
            'latitude': latitude,
            'longitude': longitude,
            'range': range_km,
            'hit_per_page': hit_per_page,
            'format': 'json'
        }
        
        # 料理ジャンルの指定
        if cuisine_type:
            params['category_l'] = self._map_cuisine_type(cuisine_type)
        
        # 予算の指定
        if budget:
            params['budget'] = self._map_budget(budget)
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            restaurants = []
            
            if 'rest' in data:
                for rest in data['rest']:
                    restaurant = {
                        'external_id': rest.get('id'),
                        'external_source': 'gurunavi',
                        'name': rest.get('name', ''),
                        'description': rest.get('pr', {}).get('pr_short', ''),
                        'cuisine_type': rest.get('category', ''),
                        'price_range': rest.get('budget', ''),
                        'location': rest.get('address', ''),
                        'address': rest.get('address', ''),
                        'phone': rest.get('tel', ''),
                        'website': rest.get('url', ''),
                        'external_rating': None,  # ぐるなびAPIには評価がない
                        'external_review_count': None,
                        'image_url': rest.get('image_url', {}).get('shop_image1', ''),
                        'latitude': rest.get('latitude'),
                        'longitude': rest.get('longitude')
                    }
                    restaurants.append(restaurant)
            
            return restaurants
            
        except requests.RequestException as e:
            logger.error(f"Gurunavi API request failed: {e}")
            return self._get_mock_restaurants()
    
    def _map_cuisine_type(self, cuisine_type: str) -> str:
        """料理ジャンルをぐるなびAPIのカテゴリにマッピング"""
        mapping = {
            '和食': 'RSFST08000',
            '洋食': 'RSFST09000',
            '中華': 'RSFST10000',
            'イタリアン': 'RSFST11000',
            'フレンチ': 'RSFST12000',
            '焼肉': 'RSFST13000',
            '居酒屋': 'RSFST14000',
            'カフェ': 'RSFST15000'
        }
        return mapping.get(cuisine_type, '')
    
    def _map_budget(self, budget: str) -> str:
        """予算をぐるなびAPIの予算コードにマッピング"""
        mapping = {
            '1000円以下': 'B009',
            '1000-2000円': 'B010',
            '2000-3000円': 'B011',
            '3000-4000円': 'B012',
            '4000-5000円': 'B013',
            '5000円以上': 'B014'
        }
        return mapping.get(budget, '')
    
    def _get_mock_restaurants(self) -> List[Dict]:
        """モックデータを返す"""
        return [
            {
                'external_id': 'mock_gurunavi_1',
                'external_source': 'gurunavi',
                'name': 'サンプル和食レストラン',
                'description': '新鮮な食材を使った本格和食',
                'cuisine_type': '和食',
                'price_range': '2000-3000円',
                'location': '東京都新宿区',
                'address': '東京都新宿区新宿1-1-1',
                'phone': '03-1234-5678',
                'website': 'https://example.com',
                'external_rating': None,
                'external_review_count': None,
                'image_url': 'https://example.com/image1.jpg',
                'latitude': 35.6895,
                'longitude': 139.6917
            }
        ]


class GooglePlacesAPIClient:
    """Google Places API連携クライアント"""
    
    def __init__(self):
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.api_key = getattr(settings, 'GOOGLE_PLACES_API_KEY', None)
    
    def search_restaurants(
        self,
        latitude: float,
        longitude: float,
        radius: int = 3000,
        restaurant_type: str = "restaurant",
        keyword: Optional[str] = None
    ) -> List[Dict]:
        """
        レストラン検索
        
        Args:
            latitude: 緯度
            longitude: 経度
            radius: 検索半径（メートル）
            restaurant_type: 場所のタイプ
            keyword: 検索キーワード
        
        Returns:
            レストラン情報のリスト
        """
        if not self.api_key:
            logger.warning("Google Places API key not configured, returning mock data")
            return self._get_mock_restaurants()
        
        # Nearby Search API
        url = f"{self.base_url}/nearbysearch/json"
        params = {
            'location': f"{latitude},{longitude}",
            'radius': radius,
            'type': restaurant_type,
            'key': self.api_key
        }
        
        if keyword:
            params['keyword'] = keyword
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            restaurants = []
            
            if 'results' in data:
                for place in data['results']:
                    restaurant = {
                        'external_id': place.get('place_id'),
                        'external_source': 'google_places',
                        'name': place.get('name', ''),
                        'description': '',  # Nearby Searchには詳細説明がない
                        'cuisine_type': self._extract_cuisine_type(place.get('types', [])),
                        'price_range': self._map_price_level(place.get('price_level')),
                        'location': place.get('vicinity', ''),
                        'address': place.get('vicinity', ''),
                        'phone': '',  # Nearby Searchには電話番号がない
                        'website': '',  # Nearby Searchにはウェブサイトがない
                        'external_rating': place.get('rating'),
                        'external_review_count': place.get('user_ratings_total'),
                        'image_url': self._get_photo_url(place.get('photos', [])),
                        'latitude': place.get('geometry', {}).get('location', {}).get('lat'),
                        'longitude': place.get('geometry', {}).get('location', {}).get('lng')
                    }
                    restaurants.append(restaurant)
            
            return restaurants
            
        except requests.RequestException as e:
            logger.error(f"Google Places API request failed: {e}")
            return self._get_mock_restaurants()
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        場所の詳細情報を取得
        
        Args:
            place_id: Google Places API の place_id
        
        Returns:
            詳細情報
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos,opening_hours',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'result' in data:
                return data['result']
            
        except requests.RequestException as e:
            logger.error(f"Google Places Details API request failed: {e}")
        
        return None
    
    def _extract_cuisine_type(self, types: List[str]) -> str:
        """場所のタイプから料理ジャンルを抽出"""
        cuisine_mapping = {
            'japanese_restaurant': '和食',
            'chinese_restaurant': '中華',
            'italian_restaurant': 'イタリアン',
            'french_restaurant': 'フレンチ',
            'korean_restaurant': '韓国料理',
            'thai_restaurant': 'タイ料理',
            'indian_restaurant': 'インド料理',
            'mexican_restaurant': 'メキシコ料理',
            'cafe': 'カフェ',
            'bar': 'バー',
            'bakery': 'ベーカリー'
        }
        
        for place_type in types:
            if place_type in cuisine_mapping:
                return cuisine_mapping[place_type]
        
        return 'レストラン'
    
    def _map_price_level(self, price_level: Optional[int]) -> str:
        """価格レベルを日本語の価格帯にマッピング"""
        if price_level is None:
            return '価格不明'
        
        mapping = {
            0: '無料',
            1: '1000円以下',
            2: '1000-3000円',
            3: '3000-5000円',
            4: '5000円以上'
        }
        return mapping.get(price_level, '価格不明')
    
    def _get_photo_url(self, photos: List[Dict]) -> str:
        """写真URLを取得"""
        if not photos or not self.api_key:
            return ''
        
        photo_reference = photos[0].get('photo_reference')
        if photo_reference:
            return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={self.api_key}"
        
        return ''
    
    def _get_mock_restaurants(self) -> List[Dict]:
        """モックデータを返す"""
        return [
            {
                'external_id': 'mock_google_1',
                'external_source': 'google_places',
                'name': 'サンプルイタリアンレストラン',
                'description': '',
                'cuisine_type': 'イタリアン',
                'price_range': '2000-3000円',
                'location': '東京都渋谷区',
                'address': '東京都渋谷区渋谷1-1-1',
                'phone': '',
                'website': '',
                'external_rating': 4.2,
                'external_review_count': 150,
                'image_url': 'https://example.com/image2.jpg',
                'latitude': 35.6598,
                'longitude': 139.7006
            }
        ]


class RestaurantSearchService:
    """レストラン検索統合サービス"""
    
    def __init__(self):
        self.gurunavi_client = GurunaviAPIClient()
        self.google_places_client = GooglePlacesAPIClient()
    
    def search_restaurants_combined(
        self,
        latitude: float,
        longitude: float,
        preferences: Dict,
        max_results: int = 20
    ) -> List[Dict]:
        """
        複数のAPIからレストラン情報を統合検索
        
        Args:
            latitude: 緯度
            longitude: 経度
            preferences: ユーザーの好み（料理ジャンル、予算など）
            max_results: 最大取得件数
        
        Returns:
            統合されたレストラン情報のリスト
        """
        all_restaurants = []
        
        # ぐるなびAPIから検索
        try:
            gurunavi_results = self.gurunavi_client.search_restaurants(
                latitude=latitude,
                longitude=longitude,
                cuisine_type=preferences.get('cuisine_type'),
                budget=preferences.get('budget'),
                hit_per_page=max_results // 2
            )
            all_restaurants.extend(gurunavi_results)
        except Exception as e:
            logger.error(f"Gurunavi search failed: {e}")
        
        # Google Places APIから検索
        try:
            google_results = self.google_places_client.search_restaurants(
                latitude=latitude,
                longitude=longitude,
                keyword=preferences.get('cuisine_type')
            )
            all_restaurants.extend(google_results)
        except Exception as e:
            logger.error(f"Google Places search failed: {e}")
        
        # 重複除去（名前と住所で判定）
        unique_restaurants = []
        seen = set()
        
        for restaurant in all_restaurants:
            key = (restaurant['name'], restaurant['location'])
            if key not in seen:
                seen.add(key)
                unique_restaurants.append(restaurant)
        
        return unique_restaurants[:max_results]

