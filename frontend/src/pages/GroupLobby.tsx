import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Layout } from '../components/Layout/Layout';
import { Button } from '../components/UI/Button';
import { LoadingSpinner } from '../components/UI/LoadingSpinner';
import { groupApi, interviewApi, recommendationApi } from '../services/api';
import { useStore } from '../store/useStore';

export const GroupLobby: React.FC = () => {
  const navigate = useNavigate();
  const { groupId } = useParams<{ groupId: string }>();
  const [searchParams] = useSearchParams();
  const userIdFromUrl = searchParams.get('userId');
  const { currentUser, currentGroup, setCurrentGroup, setCurrentUser } = useStore();
  const [isLoading, setIsLoading] = useState(false);
  const [interviewStatus, setInterviewStatus] = useState<any>(null);
  const [recommendationAvailable, setRecommendationAvailable] = useState(false);

  // デバッグ情報をコンソールに出力
  console.log('GroupLobby - groupId:', groupId);
  console.log('GroupLobby - currentUser:', currentUser);
  console.log('GroupLobby - currentGroup:', currentGroup);
  console.log('GroupLobby - currentGroup.members:', currentGroup?.members);
  console.log('GroupLobby - typeof currentGroup.members:', typeof currentGroup?.members);

  useEffect(() => {
    console.log('GroupLobby useEffect - groupId:', groupId, 'currentUser:', currentUser);
    
    if (!groupId) {
      console.log('GroupLobby - No groupId, redirecting to /');
      navigate('/');
      return;
    }

    const fetchGroup = async () => {
      try {
        console.log('GroupLobby - Fetching group for groupId:', groupId);
        console.log('GroupLobby - Current store state:', {
          currentUser: currentUser?.user_id,
          currentGroup: currentGroup?.group_id,
        });
        
        const group = await groupApi.getGroup(groupId);
        console.log('GroupLobby - Fetched group:', {
          group_id: group.group_id,
          name: group.name,
          members: group.members?.map(m => ({ user_id: m.user_id, nickname: m.nickname }))
        });
        
        setCurrentGroup(group);
        
        // ユーザー情報がない場合、URLパラメータやローカルストレージから復元を試みる
        if (!currentUser && group.members && group.members.length > 0) {
          let targetUser = null;
          
          // URLパラメータにuserIdがある場合、そのユーザーを探す
          if (userIdFromUrl) {
            targetUser = group.members.find(m => m.user_id === userIdFromUrl);
            console.log('GroupLobby - Found user from URL:', targetUser);
          }
          
          // URLパラメータにない場合、とりあえず最初のメンバーを使用
          if (!targetUser && group.members.length > 0) {
            targetUser = group.members[0];
            console.log('GroupLobby - Using first member as fallback:', targetUser);
          }
          
          if (targetUser) {
            setCurrentUser(targetUser);
          }
        }
        
        // インタビュー状況も取得
        const status = await interviewApi.getGroupInterviewStatus(groupId);
        setInterviewStatus(status);
        
        // 推薦が利用可能かチェック
        if (status.all_completed) {
          console.log('GroupLobby - All interviews completed, checking for recommendations...');
          try {
            // まず既存の推薦を取得
            const recommendations = await recommendationApi.getRecommendations(groupId);
            console.log('GroupLobby - Found existing recommendations:', recommendations);
            setRecommendationAvailable(true);
          } catch (getError: any) {
            console.log('GroupLobby - Get recommendations error:', getError.response?.status, getError.response?.data);
            if (getError.response?.status === 404) {
              // 推薦が存在しない場合、生成を試す
              try {
                console.log('GroupLobby - No existing recommendations, trying to generate...');
                const newRecommendations = await recommendationApi.generateRecommendations(groupId);
                console.log('GroupLobby - Generated new recommendations:', newRecommendations);
                setRecommendationAvailable(true);
              } catch (generateError: any) {
                console.error('GroupLobby - Failed to generate recommendations:', generateError.response?.status, generateError.response?.data);
                setRecommendationAvailable(false);
              }
            } else {
              console.error('GroupLobby - Error fetching recommendations:', getError);
              setRecommendationAvailable(false);
            }
          }
        } else {
          console.log('GroupLobby - Not all interviews completed yet');
          setRecommendationAvailable(false);
        }
      } catch (error) {
        console.error('GroupLobby - Error fetching group:', error);
        toast.error('グループ情報の取得に失敗しました');
        navigate('/');
      }
    };

    fetchGroup();

    // 3秒間隔で更新（より頻繁にチェック）
    const interval = setInterval(fetchGroup, 3000);
    return () => clearInterval(interval);
  }, [groupId, currentUser, navigate, setCurrentGroup]);

  const handleStartInterview = async () => {
    if (!currentUser || !currentGroup || isLoading) return;

    setIsLoading(true);
    try {
      // まず現在のユーザーのインタビュー状態をチェック
      console.log('Checking interview status for user:', currentUser.user_id);
      
      // インタビューを開始または再開
      console.log('Starting/resuming interview for:', currentUser.user_id, 'in group:', currentGroup.group_id);
      const interview = await interviewApi.startInterview(currentGroup.group_id, currentUser.user_id);
      console.log('Interview response:', interview);
      
      // インタビューページに遷移
      navigate(`/group/${currentGroup.group_id}/interview`);
    } catch (error: any) {
      console.error('Interview start error:', error);
      
      // エラーが400の場合の詳細を確認
      if (error.response?.status === 400) {
        console.log('400 error details:', error.response.data);
        toast.error('インタビューの状態に問題があります。ページを更新してみてください。');
      } else {
        toast.error('ヒアリング開始に失敗しました');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const copyInviteCode = () => {
    if (currentGroup) {
      navigator.clipboard.writeText(currentGroup.invite_code);
      toast.success('招待コードをコピーしました！');
    }
  };

  const copyInviteLink = () => {
    if (currentGroup) {
      const link = `${window.location.origin}/group/join?code=${currentGroup.invite_code}`;
      navigator.clipboard.writeText(link);
      toast.success('招待リンクをコピーしました！');
    }
  };

  if (!currentUser) {
    console.log('GroupLobby render - No currentUser, showing loading');
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-600">ユーザー情報を確認中...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!currentGroup) {
    console.log('GroupLobby render - No currentGroup, showing loading');
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-600">グループ情報を読み込み中...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const canStartInterview = currentGroup?.members?.length >= 2;

  return (
    <Layout>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="text-center space-y-2">
          <div className="text-4xl mb-2">👥</div>
          <h1 className="text-2xl font-bold text-gray-800">{currentGroup.name}</h1>
          {currentGroup.description && (
            <p className="text-gray-600">{currentGroup.description}</p>
          )}
        </div>

        {/* メンバー一覧 */}
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            参加メンバー ({currentGroup.members?.length || 0}/6人)
          </h2>
          <div className="space-y-3">
            {currentGroup.members && currentGroup.members.length > 0 ? (
              currentGroup.members.map((member) => (
                <div key={member.user_id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-red-400 to-red-500 text-white rounded-full flex items-center justify-center font-bold">
                      {member.nickname.charAt(0)}
                    </div>
                    <div>
                      <span className="font-medium text-gray-800">{member.nickname}</span>
                      {member.user_id === currentUser?.user_id && (
                        <span className="ml-2 text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full">あなた</span>
                      )}
                    </div>
                  </div>
                  
                  {/* インタビューステータス */}
                  <div className="flex items-center space-x-2">
                    {(() => {
                      const memberStatus = interviewStatus?.member_status?.find((status: any) => status.user_id === member.user_id);
                      const status = memberStatus?.interview_status || 'not_started';
                      
                      if (member.user_id === currentUser?.user_id) {
                        if (status === 'completed') {
                          return (
                            <span className="text-xs text-green-600 px-3 py-1 bg-green-100 rounded-full">
                              ✓ 完了
                            </span>
                          );
                        } else {
                          return (
                            <Button 
                              size="sm" 
                              onClick={handleStartInterview}
                              disabled={isLoading}
                              className="px-4 py-2 text-sm"
                            >
                              {isLoading ? <LoadingSpinner size="sm" /> : 'ヒアリング開始'}
                            </Button>
                          );
                        }
                      } else {
                        if (status === 'completed') {
                          return (
                            <span className="text-xs text-green-600 px-3 py-1 bg-green-100 rounded-full">
                              ✓ 完了
                            </span>
                          );
                        } else if (status === 'in_progress') {
                          return (
                            <span className="text-xs text-blue-600 px-3 py-1 bg-blue-100 rounded-full">
                              進行中
                            </span>
                          );
                        } else {
                          return (
                            <span className="text-xs text-gray-500 px-3 py-1 bg-gray-100 rounded-full">
                              待機中
                            </span>
                          );
                        }
                      }
                    })()}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-gray-500 text-center py-4">
                メンバー情報を読み込み中...
              </div>
            )}
          </div>
        </div>

        {/* 招待コード（主催者のみ表示） */}
        {currentUser && currentGroup && currentUser.user_id === currentGroup.host_user_id && (
          <div className="bg-gradient-to-r from-teal-50 to-blue-50 rounded-2xl p-6 border border-teal-200">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">メンバー招待</h2>
            <div className="space-y-4">
              <div className="bg-white rounded-lg p-4 border-2 border-dashed border-gray-300">
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-2">招待コード</p>
                  <p className="text-2xl font-bold text-gray-800 tracking-wider">
                    {currentGroup.invite_code}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={copyInviteCode}
                  className="text-xs"
                >
                  コードをコピー
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={copyInviteLink}
                  className="text-xs"
                >
                  リンクをコピー
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* アクション */}
        <div className="space-y-4">
          {interviewStatus?.all_completed && recommendationAvailable ? (
            <Button 
              size="lg" 
              className="w-full"
              onClick={() => {
                const userParam = currentUser?.user_id ? `?userId=${currentUser.user_id}` : '';
                navigate(`/group/${groupId}/recommendations${userParam}`);
              }}
            >
              🎯 レストラン推薦を見る
            </Button>
          ) : interviewStatus?.all_completed && !recommendationAvailable ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
              <p className="text-green-800 font-medium mb-2">✅ 全員のヒアリングが完了しました！</p>
              <p className="text-green-700 text-sm">
                AIが推薦を準備中です...しばらくお待ちください
              </p>
            </div>
          ) : canStartInterview ? (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
              <p className="text-blue-800 font-medium mb-2">💡 ヒアリング進行中</p>
              <p className="text-blue-700 text-sm">
                各メンバーが上記の「ヒアリング開始」ボタンから個別にAIインタビューを受けてください<br />
                全員完了後、レストラン推薦が表示されます
              </p>
              {interviewStatus && (
                <div className="mt-3 text-sm text-blue-600">
                  進捗: {interviewStatus.completed_interviews}/{interviewStatus.total_members}人 完了
                </div>
              )}
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
              <p className="text-yellow-800 font-medium">メンバーを待っています</p>
              <p className="text-yellow-700 text-sm mt-1">
                最低2人以上でヒアリングを開始できます
              </p>
            </div>
          )}
        </div>

        {/* 注意事項 */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <span className="text-gray-600 text-sm">📝</span>
            <div className="text-sm text-gray-700">
              <p className="font-medium mb-1">ヒアリングについて</p>
              <p>AIが個別に好みや制約をお聞きします。他のメンバーには内容は見えないので、本音でお答えください。</p>
            </div>
          </div>
        </div>

        {/* 戻るボタン */}
        <div className="text-center">
          <button 
            onClick={() => navigate('/')}
            className="text-gray-500 hover:text-gray-700 text-sm transition-colors duration-200"
          >
            ← トップページに戻る
          </button>
        </div>
      </div>
    </Layout>
  );
};