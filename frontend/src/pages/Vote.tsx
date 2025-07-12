import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Layout } from '../components/Layout/Layout';
import { Button } from '../components/UI/Button';
import { LoadingSpinner } from '../components/UI/LoadingSpinner';
import { useStore } from '../store/useStore';
import { voteApi, recommendationApi } from '../services/api';

export const Vote: React.FC = () => {
  const navigate = useNavigate();
  const { groupId } = useParams<{ groupId: string }>();
  const { currentUser, currentGroup, currentRecommendation } = useStore();
  const [votes, setVotes] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const handleFinalDecision = async (restaurant: any) => {
    if (!currentUser || !currentGroup || !groupId) {
      toast.error('必要な情報が不足しています');
      return;
    }

    try {
      await recommendationApi.setFinalDecision(
        groupId,
        restaurant.restaurant_id,
        restaurant.name,
        currentUser.user_id
      );
      
      toast.success(`${restaurant.name}に決定しました！`);
      navigate(`/group/${groupId}/result`, { state: { winner: restaurant } });
    } catch (error) {
      console.error('Final decision error:', error);
      toast.error('決定に失敗しました');
    }
  };

  useEffect(() => {
    console.log('Vote.tsx - useEffect triggered with:', {
      groupId,
      currentUser: currentUser?.user_id,
      currentGroup: currentGroup?.group_id,
      currentRecommendation: currentRecommendation?.recommendation_id
    });
    
    if (!groupId || !currentUser || !currentGroup || !currentRecommendation) {
      console.log('Vote.tsx - Missing data, redirecting to home');
      navigate('/');
      return;
    }

    const fetchVotes = async () => {
      try {
        console.log('Vote.tsx - Fetching votes for groupId:', groupId);
        const voteData = await voteApi.getGroupVotes(groupId);
        console.log('Vote.tsx - Raw vote data:', voteData);
        console.log('Vote.tsx - voted_members:', voteData.voted_members);
        console.log('Vote.tsx - total_members:', voteData.total_members);
        console.log('Vote.tsx - is_voting_complete:', voteData.is_voting_complete);
        setVotes(voteData);
        
        // 最終決定があったかチェック（主催者以外）
        if (currentUser && currentGroup && currentUser.user_id !== currentGroup.host_user_id) {
          try {
            const finalDecision = await recommendationApi.getFinalDecision(groupId);
            if (finalDecision.has_final_decision) {
              const restaurantData = finalDecision.final_decision;
              // 推薦データから該当するレストランを探す
              const selectedRestaurant = currentRecommendation?.restaurants.find(
                r => r.restaurant_id === restaurantData.restaurant_id
              );
              
              if (selectedRestaurant) {
                toast.success(`${restaurantData.restaurant_name}に決定されました！`);
                navigate(`/group/${groupId}/result`, { state: { winner: selectedRestaurant } });
                return;
              }
            }
          } catch (finalDecisionError) {
            // 最終決定チェックエラーは無視（まだ決定されていない）
            console.log('Final decision not yet made');
          }
        }
        
        // 自動遷移は削除（主催者の決定を待つ）
      } catch (error) {
        console.error('Vote fetch error:', error);
        toast.error('投票結果の取得に失敗しました');
      } finally {
        setIsLoading(false);
      }
    };

    fetchVotes();
    
    // 投票完了まで10秒間隔で投票結果を更新
    const interval = setInterval(() => {
      if (votes?.is_voting_complete) {
        clearInterval(interval);
        return;
      }
      fetchVotes();
    }, 10000);
    
    return () => clearInterval(interval);
  }, [groupId, navigate, currentUser, currentGroup, currentRecommendation]); // 依存配列を更新

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
          <p className="ml-4 text-gray-600">投票結果を読み込み中...</p>
        </div>
      </Layout>
    );
  }

  if (!currentRecommendation || !votes) {
    return (
      <Layout>
        <div className="text-center py-8">
          <p className="text-gray-600">投票情報が見つかりません</p>
          <Button onClick={() => navigate(`/group/${groupId}/recommendations`)} className="mt-4">
            推薦に戻る
          </Button>
        </div>
      </Layout>
    );
  }

  // APIから取得した投票者数を使用
  const votedMembers = votes.voted_members || 0;
  const totalMembers = votes.total_members || currentGroup?.members.length || 0;
  const isVotingComplete = votes.is_voting_complete || votedMembers >= totalMembers;

  return (
    <Layout>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="text-center space-y-2">
          <div className="text-4xl mb-2">🗳️</div>
          <h1 className="text-2xl font-bold text-gray-800">投票結果</h1>
          <p className="text-gray-600">
            投票進捗: {votedMembers}/{totalMembers}人
          </p>
        </div>

        {/* 投票進捗バー */}
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">投票進捗</span>
            <span className="text-sm text-gray-500">{votedMembers}/{totalMembers}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-red-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min((votedMembers / totalMembers) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* 投票結果一覧 */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">各店舗への投票数</h2>
          
          {votes.vote_results && votes.vote_results
            .sort((a: any, b: any) => (b.vote_summary.like || 0) - (a.vote_summary.like || 0))
            .map((result: any) => {
              const restaurant = currentRecommendation.restaurants.find(r => r.restaurant_id === result.candidate_id);
              if (!restaurant) return null;
              
              const voteCount = result.vote_summary.like || 0;
              const percentage = totalMembers > 0 ? (voteCount / totalMembers) * 100 : 0;
              
              return (
                <div key={result.candidate_id} className="bg-white rounded-2xl shadow-lg overflow-hidden">
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-800 mb-2">{restaurant.name}</h3>
                        <div className="flex flex-wrap gap-2 mb-2">
                          <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-medium">
                            {restaurant.cuisine_type}
                          </span>
                          <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
                            {restaurant.price_range}
                          </span>
                        </div>
                        <p className="text-gray-600 text-sm">{restaurant.address}</p>
                      </div>
                      
                      <div className="text-right">
                        <div className="text-3xl font-bold text-red-500">{voteCount}</div>
                        <div className="text-sm text-gray-500">票</div>
                      </div>
                    </div>
                    
                    {/* 投票バー */}
                    <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                      <div 
                        className="bg-red-500 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                    
                    <div className="text-right text-sm text-gray-500">
                      {percentage.toFixed(1)}% ({voteCount}/{totalMembers}人)
                    </div>
                    
                    {/* 主催者用の決定ボタン */}
                    {currentUser && currentGroup && currentUser.user_id === currentGroup.host_user_id && isVotingComplete && (
                      <div className="mt-4">
                        <Button 
                          size="md"
                          variant="primary"
                          className="w-full"
                          onClick={() => handleFinalDecision(restaurant)}
                        >
                          この店に決定する
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
        </div>

        {/* 投票が完了した場合の表示 */}
        {isVotingComplete && (
          <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-2xl p-6 border-2 border-blue-200">
            <div className="text-center space-y-4">
              <div className="text-4xl">✅</div>
              <h2 className="text-2xl font-bold text-gray-800">投票が完了しました</h2>
              
              {/* 主催者向けのメッセージ */}
              {currentUser && currentGroup && currentUser.user_id === currentGroup.host_user_id && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
                  <p className="text-yellow-800 font-medium">⬆️ 上記の各店舗から最終決定してください</p>
                  <p className="text-yellow-700 text-sm mt-1">
                    どの店舗でも選択できます
                  </p>
                </div>
              )}
              
              {/* 主催者ではない場合のメッセージ */}
              {currentUser && currentGroup && currentUser.user_id !== currentGroup.host_user_id && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                  <p className="text-blue-800 font-medium">投票が完了しました</p>
                  <p className="text-blue-700 text-sm mt-1">
                    主催者が最終決定するまでお待ちください
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* まだ投票が完了していない場合 */}
        {!isVotingComplete && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <p className="text-blue-800 font-medium">投票を待っています</p>
            <p className="text-blue-700 text-sm mt-1">
              すべてのメンバーが投票するまでお待ちください
            </p>
          </div>
        )}

        {/* 戻るボタン */}
        <div className="text-center">
          <button 
            onClick={() => navigate(`/group/${groupId}/recommendations`)}
            className="text-gray-500 hover:text-gray-700 text-sm transition-colors duration-200"
          >
            ← 推薦に戻る
          </button>
        </div>
      </div>
    </Layout>
  );
};
