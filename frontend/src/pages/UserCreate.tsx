import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Layout } from '../components/Layout/Layout';
import { Button } from '../components/UI/Button';
import { Input } from '../components/UI/Input';
import { LoadingSpinner } from '../components/UI/LoadingSpinner';
import { userApi } from '../services/api';
import { useStore } from '../store/useStore';
import { CreateUserRequest } from '../types';

export const UserCreate: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const action = searchParams.get('action') || 'create';
  const inviteCode = searchParams.get('code'); // 招待コードを取得
  const { setCurrentUser } = useStore();
  const [isLoading, setIsLoading] = useState(false);

  const { control, register, handleSubmit, formState: { errors } } = useForm<CreateUserRequest>();

  const onSubmit = async (data: CreateUserRequest) => {
    setIsLoading(true);
    try {
      const user = await userApi.createAnonymousUser(data);
      setCurrentUser(user);
      
      toast.success(`${data.nickname}さん、ようこそ！`);
      
      if (action === 'create') {
        navigate('/group/create');
      } else if (inviteCode) {
        // 招待コードがある場合は直接グループ参加ページに遷移
        navigate(`/group/join?code=${inviteCode}`);
      } else {
        navigate('/group/join');
      }
    } catch (error) {
      toast.error('ユーザー作成に失敗しました');
      console.error('User creation error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const title = action === 'create' ? 'グループを作成' : 'グループに参加';
  const description = action === 'create' 
    ? 'まずはあなたのニックネームを教えてください' 
    : 'グループに参加するためにニックネームを入力してください';

  return (
    <Layout>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="text-center space-y-2">
          <div className="text-4xl mb-2">{action === 'create' ? '👥' : '🚀'}</div>
          <h1 className="text-2xl font-bold text-gray-800">{title}</h1>
          <p className="text-gray-600">{description}</p>
        </div>

        {/* フォーム */}
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <Controller
              name="nickname"
              control={control}
              rules={{
                required: 'ニックネームは必須です',
                maxLength: { value: 20, message: '20文字以内で入力してください' }
              }}
              render={({ field }) => (
                <Input
                  label="ニックネーム"
                  placeholder="例: たろう"
                  value={field.value || ''}
                  onChange={field.onChange}
                  error={errors.nickname?.message}
                  required
                />
              )}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                食べ物の好み（任意）
              </label>
              <textarea
                {...register('preferences')}
                placeholder="例: 辛いものが好き、魚介類が苦手、予算は3000円まで"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-200 resize-none"
                rows={4}
              />
              <p className="text-xs text-gray-500 mt-1">
                事前に好みを書いておくと、AIがより良い提案をしてくれます
              </p>
            </div>

            <Button 
              type="submit" 
              size="lg" 
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? <LoadingSpinner size="sm" /> : '次に進む'}
            </Button>
          </form>
        </div>

        {/* 注意事項 */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <span className="text-yellow-600 text-sm">💡</span>
            <div className="text-sm text-yellow-800">
              <p className="font-medium mb-1">プライバシーについて</p>
              <p>ニックネームのみで参加でき、個人情報は一切収集しません。安心してご利用ください。</p>
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