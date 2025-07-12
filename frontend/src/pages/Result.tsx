import React, { useEffect } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { Button } from '../components/UI/Button';
import { useStore } from '../store/useStore';
import { Restaurant } from '../types';

export const Result: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { groupId } = useParams<{ groupId: string }>();
  const { currentUser, currentGroup } = useStore();
  
  const winner = location.state?.winner as Restaurant;

  useEffect(() => {
    if (!groupId || !currentUser || !currentGroup || !winner) {
      navigate('/');
      return;
    }
  }, [groupId, currentUser, currentGroup, winner, navigate]);

  const handleGoToLobby = () => {
    navigate(`/group/${groupId}/lobby`);
  };

  const handleCreateNewGroup = () => {
    navigate('/group/create');
  };

  if (!winner) {
    return null;
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="text-center space-y-4">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-3xl font-bold text-gray-800">決定しました！</h1>
          <p className="text-lg text-gray-600">
            {currentGroup?.name}の選択は...
          </p>
        </div>

        {/* 決定されたレストラン */}
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl p-8 border-2 border-yellow-300 shadow-lg">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-red-500 text-white rounded-full flex items-center justify-center font-bold text-2xl mx-auto">
              👑
            </div>
            
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">{winner.name}</h2>
              <div className="flex flex-wrap justify-center gap-2 mb-3">
                <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-medium">
                  {winner.cuisine_type}
                </span>
                <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
                  {winner.price_range}
                </span>
              </div>
              <p className="text-gray-600 mb-4">{winner.address}</p>
              
              {/* 評価 */}
              <div className="flex items-center justify-center space-x-2">
                <div className="flex items-center">
                  <span className="text-yellow-500 text-xl">⭐</span>
                  <span className="font-semibold ml-1">{winner.external_rating}</span>
                </div>
                <span className="text-gray-500 text-sm">
                  ({winner.external_review_count}件の口コミ)
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* おめでとうメッセージ */}
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6 text-center">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">🎊 おめでとうございます！</h3>
          <p className="text-blue-700">
            みんなで決めたお店で、素敵な時間をお過ごしください。<br />
            きっと美味しい料理と楽しい会話が待っています！
          </p>
        </div>

        {/* アクションボタン */}
        <div className="space-y-4">
          <Button
            size="lg"
            className="w-full"
            onClick={handleGoToLobby}
          >
            グループロビーに戻る
          </Button>
          
          <Button
            variant="outline"
            size="lg"
            className="w-full"
            onClick={handleCreateNewGroup}
          >
            新しいグループを作成
          </Button>
        </div>

        {/* 感謝メッセージ */}
        <div className="text-center text-gray-500 text-sm">
          <p>tabegoeをご利用いただき、ありがとうございました！</p>
        </div>
      </div>
    </Layout>
  );
};
