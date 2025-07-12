import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Layout } from '../components/Layout/Layout';
import { Button } from '../components/UI/Button';
import { Input } from '../components/UI/Input';
import { LoadingSpinner } from '../components/UI/LoadingSpinner';
import { groupApi } from '../services/api';
import { useStore } from '../store/useStore';
import { JoinGroupRequest } from '../types';

export const GroupJoin: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { currentUser, setCurrentGroup } = useStore();
  const [isLoading, setIsLoading] = useState(false);

  const { control, handleSubmit, setValue, formState: { errors } } = useForm<JoinGroupRequest>();

  useEffect(() => {
    const inviteCode = searchParams.get('code');
    
    if (!currentUser) {
      // ユーザーが未作成の場合、招待コードをパラメータに含めて遷移
      const userCreateUrl = inviteCode 
        ? `/user/create?action=join&code=${inviteCode}` 
        : '/user/create?action=join';
      navigate(userCreateUrl);
      return;
    }

    // URLパラメータから招待コードを取得
    if (inviteCode) {
      setValue('invite_code', inviteCode);
      
      // 招待コードがある場合は自動参加を試行
      const autoJoin = async () => {
        setIsLoading(true);
        try {
          const joinData = {
            invite_code: inviteCode,
            user_id: currentUser.user_id
          };
          const group = await groupApi.joinGroup(joinData);
          setCurrentGroup(group);
          
          toast.success('グループに参加しました！');
          navigate(`/group/${group.group_id}/lobby?userId=${currentUser.user_id}`);
        } catch (error) {
          // 自動参加に失敗した場合はそのまま入力画面を表示
          console.log('Auto-join failed, showing manual input form');
        } finally {
          setIsLoading(false);
        }
      };
      
      autoJoin();
    }
  }, [currentUser, navigate, searchParams, setValue, setCurrentGroup]);

  const onSubmit = async (data: JoinGroupRequest) => {
    if (!currentUser) {
      toast.error('ユーザー情報が見つかりません');
      return;
    }

    setIsLoading(true);
    try {
      const joinData = {
        ...data,
        user_id: currentUser.user_id
      };
      const group = await groupApi.joinGroup(joinData);
      setCurrentGroup(group);
      
      toast.success('グループに参加しました！');
      // グループロビーにリダイレクト
      navigate(`/group/${group.group_id}/lobby?userId=${currentUser.user_id}`);
    } catch (error) {
      toast.error('グループ参加に失敗しました。招待コードを確認してください。');
      console.error('Group join error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentUser) {
    return null;
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="text-center space-y-2">
          <div className="text-4xl mb-2">🚀</div>
          <h1 className="text-2xl font-bold text-gray-800">グループに参加</h1>
          <p className="text-gray-600">
            こんにちは、{currentUser.nickname}さん！<br />
            招待コードを入力してください
          </p>
        </div>

        {/* フォーム */}
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <Controller
              name="invite_code"
              control={control}
              rules={{
                required: '招待コードは必須です',
                pattern: {
                  value: /^[A-Z0-9]{6}$/,
                  message: '6桁の英数字を入力してください'
                }
              }}
              render={({ field }) => (
                <Input
                  label="招待コード"
                  placeholder="例: ABC123"
                  value={field.value || ''}
                  onChange={field.onChange}
                  error={errors.invite_code?.message}
                  required
                />
              )}
            />

            <Button 
              type="submit" 
              size="lg" 
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? <LoadingSpinner size="sm" /> : 'グループに参加'}
            </Button>
          </form>
        </div>

        {/* ヘルプ */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <span className="text-gray-600 text-sm">💡</span>
            <div className="text-sm text-gray-700">
              <p className="font-medium mb-1">招待コードについて</p>
              <ul className="space-y-1 list-disc list-inside">
                <li>グループ作成者から共有される6桁のコードです</li>
                <li>大文字・小文字は区別されません</li>
                <li>コードが見つからない場合は作成者に確認してください</li>
              </ul>
            </div>
          </div>
        </div>

        {/* 戻るボタン */}
        <div className="text-center">
          <button 
            onClick={() => navigate('/user/create?action=join')}
            className="text-gray-500 hover:text-gray-700 text-sm transition-colors duration-200"
          >
            ← 前に戻る
          </button>
        </div>
      </div>
    </Layout>
  );
};
