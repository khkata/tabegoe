import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Layout } from '../components/Layout/Layout';
import { Button } from '../components/UI/Button';
import { Input } from '../components/UI/Input';
import { LoadingSpinner } from '../components/UI/LoadingSpinner';
import { groupApi } from '../services/api';
import { useStore } from '../store/useStore';
import { CreateGroupRequest } from '../types';

export const GroupCreate: React.FC = () => {
  const navigate = useNavigate();
  const { currentUser, setCurrentGroup } = useStore();
  const [isLoading, setIsLoading] = useState(false);

  const { control, register, handleSubmit, formState: { errors } } = useForm<CreateGroupRequest>();

  const onSubmit = async (data: CreateGroupRequest) => {
    if (!currentUser) {
      toast.error('ユーザー情報が見つかりません');
      navigate('/user/create?action=create');
      return;
    }

    setIsLoading(true);
    try {
      const groupData = {
        ...data,
        host_user_id: currentUser.user_id
      };
      const group = await groupApi.createGroup(groupData);
      setCurrentGroup(group);
      
      toast.success('グループを作成しました！');
      navigate(`/group/${group.group_id}/lobby?userId=${currentUser.user_id}`);
    } catch (error) {
      toast.error('グループ作成に失敗しました');
      console.error('Group creation error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentUser) {
    navigate('/user/create?action=create');
    return null;
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="text-center space-y-2">
          <div className="text-4xl mb-2">🏠</div>
          <h1 className="text-2xl font-bold text-gray-800">グループを作成</h1>
          <p className="text-gray-600">
            こんにちは、{currentUser.nickname}さん！<br />
            グループの詳細を入力してください
          </p>
        </div>

        {/* フォーム */}
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <Controller
              name="name"
              control={control}
              rules={{
                required: 'グループ名は必須です',
                maxLength: { value: 50, message: '50文字以内で入力してください' }
              }}
              render={({ field }) => (
                <Input
                  label="グループ名"
                  placeholder="例: 同僚ランチ会、友達ディナー"
                  value={field.value || ''}
                  onChange={field.onChange}
                  error={errors.name?.message}
                  required
                />
              )}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                説明（任意）
              </label>
              <textarea
                {...register('description')}
                placeholder="例: 新年会の店探し、歓送迎会の会場決め"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-200 resize-none"
                rows={3}
              />
            </div>

            <Button 
              type="submit" 
              size="lg" 
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? <LoadingSpinner size="sm" /> : 'グループを作成'}
            </Button>
          </form>
        </div>

        {/* 注意事項 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <span className="text-blue-600 text-sm">ℹ️</span>
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">グループ作成後</p>
              <p>招待コードが発行されます。メンバーにコードを共有して参加してもらいましょう。</p>
            </div>
          </div>
        </div>

        {/* 戻るボタン */}
        <div className="text-center">
          <button 
            onClick={() => navigate('/user/create?action=create')}
            className="text-gray-500 hover:text-gray-700 text-sm transition-colors duration-200"
          >
            ← 前に戻る
          </button>
        </div>
      </div>
    </Layout>
  );
};