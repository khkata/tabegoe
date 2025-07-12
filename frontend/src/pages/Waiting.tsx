import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { LoadingSpinner } from '../components/UI/LoadingSpinner';
import { groupApi } from '../services/api';
import { useStore } from '../store/useStore';

export const Waiting: React.FC = () => {
  const navigate = useNavigate();
  const { groupId } = useParams<{ groupId: string }>();
  const { currentUser, currentGroup, setCurrentGroup } = useStore();
  const [completedMembers, setCompletedMembers] = useState<string[]>([]);

  useEffect(() => {
    if (!groupId || !currentUser || !currentGroup) {
      navigate('/');
      return;
    }

    const checkStatus = async () => {
      try {
        const group = await groupApi.getGroup(groupId);
        setCurrentGroup(group);
        
        // TODO: 実際のAPIでヒアリング完了状況を取得
        // 仮の実装として、3秒後にレコメンデーション画面に遷移
        setTimeout(() => {
          navigate(`/group/${groupId}/recommendations`);
        }, 3000);
      } catch (error) {
        console.error('Status check error:', error);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 2000);
    return () => clearInterval(interval);
  }, [groupId, currentUser, navigate, setCurrentGroup, currentGroup]);

  if (!currentGroup) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    );
  }

  const totalMembers = currentGroup.members.length;
  const progress = (completedMembers.length / totalMembers) * 100;

  return (
    <Layout>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="text-center space-y-2">
          <div className="text-4xl mb-2">⏳</div>
          <h1 className="text-2xl font-bold text-gray-800">ヒアリング完了を待機中</h1>
          <p className="text-gray-600">
            他のメンバーのヒアリングが完了するまでお待ちください
          </p>
        </div>

        {/* 進捗表示 */}
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">進捗状況</h2>
          
          {/* プログレスバー */}
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>完了</span>
              <span>{completedMembers.length}/{totalMembers}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-red-500 to-red-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          {/* メンバー状況 */}
          <div className="space-y-3">
            {currentGroup.members.map((member) => {
              const isCompleted = completedMembers.includes(member.user_id);
              const isCurrentUser = member.user_id === currentUser?.user_id;
              
              return (
                <div key={member.user_id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-red-400 to-red-500 text-white rounded-full flex items-center justify-center font-bold">
                      {member.nickname.charAt(0)}
                    </div>
                    <div>
                      <span className="font-medium text-gray-800">{member.nickname}</span>
                      {isCurrentUser && (
                        <span className="ml-2 text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full">あなた</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center">
                    {isCompleted ? (
                      <span className="text-green-600 text-sm font-medium">✓ 完了</span>
                    ) : isCurrentUser ? (
                      <span className="text-green-600 text-sm font-medium">✓ 完了</span>
                    ) : (
                      <span className="text-yellow-600 text-sm">⏳ 実行中</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 待機メッセージ */}
        <div className="bg-gradient-to-r from-blue-50 to-teal-50 rounded-2xl p-6 border border-blue-200">
          <div className="text-center space-y-3">
            <div className="text-2xl">☕</div>
            <h3 className="font-semibold text-gray-800">少々お待ちください</h3>
            <p className="text-sm text-gray-600">
              全員のヒアリングが完了次第、AIがおすすめのレストランを分析して提案いたします。
            </p>
          </div>
        </div>

        {/* アニメーション */}
        <div className="flex justify-center">
          <div className="flex space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-bounce"></div>
            <div className="w-3 h-3 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-3 h-3 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>

        {/* 戻るボタン */}
        <div className="text-center">
          <button 
            onClick={() => navigate(`/group/${groupId}/lobby`)}
            className="text-gray-500 hover:text-gray-700 text-sm transition-colors duration-200"
          >
            ← グループに戻る
          </button>
        </div>
      </div>
    </Layout>
  );
};