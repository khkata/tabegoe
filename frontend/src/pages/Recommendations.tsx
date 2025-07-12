import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Layout } from '../components/Layout/Layout';
import { Button } from '../components/UI/Button';
import { LoadingSpinner } from '../components/UI/LoadingSpinner';
import { recommendationApi, voteApi } from '../services/api';
import { useStore } from '../store/useStore';
import { Restaurant } from '../types';

export const Recommendations: React.FC = () => {
  const navigate = useNavigate();
  const { groupId } = useParams<{ groupId: string }>();
  const [searchParams] = useSearchParams();
  const userIdFromUrl = searchParams.get('userId');
  const { currentUser, currentGroup, currentRecommendation, setCurrentRecommendation, setCurrentUser } = useStore();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedRestaurant, setSelectedRestaurant] = useState<string | null>(null);
  const [isNavigating, setIsNavigating] = useState(false);
  const [userVoteStatus, setUserVoteStatus] = useState<any>(null);
  const [isVoting, setIsVoting] = useState(false);
  const [interviewStatus, setInterviewStatus] = useState<any>(null);

  useEffect(() => {
    console.log('Recommendations.tsx - useEffect with params:', {
      groupId,
      currentUser: currentUser?.user_id,
      currentGroup: currentGroup?.group_id,
      currentRecommendation: currentRecommendation?.recommendation_id
    });
    
    if (!groupId || !currentUser || !currentGroup) {
      console.log('Recommendations.tsx - Missing required data, redirecting to home');
      navigate('/');
      return;
    }

    let isCancelled = false; // クリーンアップフラグ

    const fetchRecommendations = async () => {
      if (isCancelled) return; // キャンセルされていたら処理を中断
      
      setIsLoading(true);
      try {
        // 常に現在のグループIDで最新のrecommendationを取得
        console.log('Recommendations.tsx - Fetching for groupId:', groupId);
        let recommendation;
        
        try {
          // まず既存のrecommendationを取得を試す
          recommendation = await recommendationApi.getRecommendations(groupId);
          console.log('Recommendations.tsx - Found existing recommendation:', recommendation);
        } catch (error: any) {
          if (isCancelled) return; // キャンセルされていたら処理を中断
          
          // 404の場合のみ新しく生成、その他のエラーは再スロー
          if (error.response?.status === 404) {
            try {
              console.log('Recommendations.tsx - No existing recommendation, generating new one');
              recommendation = await recommendationApi.generateRecommendations(groupId);
              console.log('Recommendations.tsx - Generated new recommendation:', recommendation);
            } catch (generateError: any) {
              if (!isCancelled) {
                if (generateError.response?.status === 400 && 
                    generateError.response?.data?.detail?.includes('All members must complete')) {
                  // 全員のインタビューが完了していない場合はロビーに戻る（エラーメッセージなし）
                  console.log('Recommendations.tsx - Not all interviews completed, returning to lobby');
                  const userParam = currentUser?.user_id ? `?userId=${currentUser.user_id}` : '';
                  navigate(`/group/${groupId}/lobby${userParam}`);
                  return;
                } else {
                  console.error('Recommendations.tsx - Generate error:', generateError);
                  throw generateError;
                }
              }
            }
          } else {
            throw error; // 404以外のエラーは再スロー
          }
        }
        
        if (!isCancelled) { // キャンセルされていない場合のみ状態を更新
          if (recommendation) {
            setCurrentRecommendation(recommendation);
            
            // インタビュー状況を取得
            try {
              const status = await recommendationApi.getInterviewStatus(groupId);
              console.log('Recommendations.tsx - Interview status:', status);
              setInterviewStatus(status);
            } catch (error) {
              console.log('Failed to fetch interview status:', error);
            }
            
            // ユーザーの投票状態も取得
            try {
              const voteStatus = await voteApi.getUserVote(groupId, currentUser.user_id);
              console.log('Recommendations.tsx - User vote status:', voteStatus);
              setUserVoteStatus(voteStatus);
              if (voteStatus.has_voted) {
                setSelectedRestaurant(voteStatus.voted_candidate_id);
              }
            } catch (error) {
              console.log('Failed to fetch user vote status:', error);
              // 投票状態の取得に失敗してもrecommendationの表示は続行
            }
          } else {
            // recommendationが取得できない場合はロビーに戻る
            console.log('Recommendations.tsx - No recommendation available, returning to lobby');
            const userParam = currentUser?.user_id ? `?userId=${currentUser.user_id}` : '';
            navigate(`/group/${groupId}/lobby${userParam}`);
            return;
          }
        }
      } catch (error) {
        if (!isCancelled) { // キャンセルされていない場合のみエラー処理
          console.error('Recommendations error:', error);
          // エラーが発生した場合はロビーに戻る（エラーメッセージは表示しない）
          const userParam = currentUser?.user_id ? `?userId=${currentUser.user_id}` : '';
          navigate(`/group/${groupId}/lobby${userParam}`);
          return;
        }
      } finally {
        if (!isCancelled) { // キャンセルされていない場合のみローディング終了
          setIsLoading(false);
        }
      }
    };

    fetchRecommendations();

    // クリーンアップ関数
    return () => {
      isCancelled = true;
    };
  }, [groupId, navigate]); // currentRecommendationを依存配列から削除

  const handleVote = async (restaurantId: string) => {
    if (!currentUser || !groupId) {
      toast.error('ユーザー情報が見つかりません');
      return;
    }

    // 投票処理中は重複クリックを防ぐ
    if (isVoting) {
      console.log('Recommendations.tsx - Voting in progress, ignoring click');
      return;
    }

    // 既に投票済みの場合は確認ダイアログを表示
    if (userVoteStatus?.has_voted && userVoteStatus.voted_candidate_id !== restaurantId) {
      const confirmed = window.confirm('既に他のお店に投票済みです。投票を変更しますか？');
      if (!confirmed) {
        return;
      }
    }

    try {
      console.log('Recommendations.tsx - Voting for:', {
        restaurantId,
        userId: currentUser.user_id,
        voteType: 'like',
        timestamp: new Date().toISOString()
      });
      
      setIsVoting(true); // 投票処理中フラグを設定
      
      const result = await voteApi.voteForCandidate(restaurantId, 'like', currentUser.user_id);
      console.log('Recommendations.tsx - Vote result:', result);
      
      // 投票状態を更新
      setSelectedRestaurant(restaurantId);
      setUserVoteStatus({
        has_voted: true,
        voted_candidate_id: restaurantId,
        vote_type: 'like',
        vote_id: result.vote_id
      });
      
      toast.success('投票しました！');
      
      // 投票後、少し待ってから投票結果ページに自動遷移
      setTimeout(() => {
        navigate(`/group/${groupId}/vote`);
      }, 1500);
    } catch (error: any) {
      console.error('Recommendations.tsx - Vote error:', error);
      console.error('Recommendations.tsx - Error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message
      });
      
      if (error.response?.status === 404) {
        toast.error('レストランまたはユーザーが見つかりません');
      } else if (error.response?.status === 400) {
        toast.error('投票データが無効です');
      } else {
        toast.error('投票に失敗しました');
      }
    } finally {
      setIsVoting(false); // 投票処理中フラグを解除
    }
  };

  const goToVoting = async () => {
    if (isNavigating) return; // 重複ナビゲーションを防ぐ
    
    console.log('Navigating to vote page for group:', groupId);
    setIsNavigating(true);
    
    try {
      // 少し待ってからナビゲートすることで、状態の同期を確実にする
      await new Promise(resolve => setTimeout(resolve, 100));
      navigate(`/group/${groupId}/vote`);
    } catch (error) {
      console.error('Navigation error:', error);
      setIsNavigating(false);
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex flex-col justify-center items-center h-64 space-y-4">
          <LoadingSpinner size="lg" />
          <div className="text-center">
            <p className="text-lg font-medium text-gray-800">AI分析中...</p>
            <p className="text-sm text-gray-600">みんなの希望を考慮したお店を探しています</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!currentRecommendation) {
    return (
      <Layout>
        <div className="text-center py-8">
          <p className="text-gray-600">レストラン推薦が見つかりません</p>
          <Button onClick={() => {
            const userParam = currentUser?.user_id ? `?userId=${currentUser.user_id}` : '';
            navigate(`/group/${groupId}/lobby${userParam}`);
          }} className="mt-4">
            グループに戻る
          </Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="text-center space-y-2">
          <div className="text-4xl mb-2">🎯</div>
          <h1 className="text-2xl font-bold text-gray-800">おすすめレストラン</h1>
          <p className="text-gray-600">
            {currentGroup?.name}のメンバーにぴったりのお店です
          </p>
        </div>

        {/* 推薦理由 */}
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl p-6 border border-yellow-200">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">🤖 AIの分析結果</h2>
          <p className="text-gray-700 text-sm leading-relaxed">
            {currentRecommendation.reasoning}
          </p>
        </div>

        {/* レストラン一覧 */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">候補のお店</h2>
          
          {currentRecommendation?.restaurants?.length > 0 ? (
            currentRecommendation.restaurants.map((restaurant, index) => (
              <div key={restaurant.restaurant_id} className="bg-white rounded-2xl shadow-lg overflow-hidden">
              {/* 順位バッジ */}
              <div className="relative">
                <div className="absolute top-4 left-4 z-10">
                  <div className="w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center font-bold text-sm">
                    {index + 1}
                  </div>
                </div>
                
                {/* 画像 */}
                <div className="h-40 bg-gradient-to-r from-gray-200 to-gray-300 flex items-center justify-center">
                  {restaurant.image_url ? (
                    <img 
                      src={restaurant.image_url} 
                      alt={restaurant.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-4xl">🍽️</span>
                  )}
                </div>
              </div>

              <div className="p-6">
                {/* 店名・情報 */}
                <div className="mb-4">
                  <h3 className="text-xl font-bold text-gray-800 mb-2">{restaurant.name}</h3>
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-medium">
                      {restaurant.cuisine_type}
                    </span>
                    <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
                      {restaurant.price_range}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mb-3">{restaurant.address}</p>
                  
                  {/* 評価 */}
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center">
                      <span className="text-yellow-500">⭐</span>
                      <span className="font-semibold ml-1">{restaurant.external_rating}</span>
                    </div>
                    <span className="text-gray-500 text-sm">
                      ({restaurant.external_review_count}件の口コミ)
                    </span>
                  </div>
                </div>

                {/* 投票ボタン */}
                <Button
                  variant={selectedRestaurant === restaurant.restaurant_id ? 'secondary' : 'primary'}
                  size="lg"
                  className="w-full"
                  onClick={() => handleVote(restaurant.restaurant_id)}
                  disabled={isVoting}
                >
                  {isVoting && selectedRestaurant === restaurant.restaurant_id 
                    ? '投票中...' 
                    : selectedRestaurant === restaurant.restaurant_id 
                    ? '✓ 投票済み' 
                    : 'このお店に投票'}
                </Button>
              </div>
            </div>
            ))
          ) : (
            <div className="bg-white rounded-2xl p-8 text-center">
              <p className="text-gray-500">レストランの推薦を生成中です...</p>
              <LoadingSpinner size="lg" />
            </div>
          )}
        </div>

        {/* アクション */}
        <div className="space-y-4">
          <Button
            variant="secondary"
            size="lg"
            className="w-full"
            onClick={goToVoting}
            disabled={isNavigating}
          >
            {isNavigating ? '読み込み中...' : '投票結果を見る'}
          </Button>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <span className="text-blue-600 text-sm">💡</span>
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">投票について</p>
                <p>お気に入りのお店を1つ選んで投票してください。みんなの投票が集まったら最終決定します。</p>
              </div>
            </div>
          </div>
        </div>

        {/* 戻るボタン */}
        <div className="text-center">
          <button 
            onClick={() => {
              const userParam = currentUser?.user_id ? `?userId=${currentUser.user_id}` : '';
              navigate(`/group/${groupId}/lobby${userParam}`);
            }}
            className="text-gray-500 hover:text-gray-700 text-sm transition-colors duration-200"
          >
            ← グループに戻る
          </button>
        </div>
      </div>
    </Layout>
  );
};