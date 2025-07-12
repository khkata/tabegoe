import React from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { Button } from '../components/UI/Button';

export const Landing: React.FC = () => {
  return (
    <Layout>
      <div className="text-center space-y-8">
        {/* ヘロー部分 */}
        <div className="space-y-4">
          <div className="text-6xl mb-4">🍽️</div>
          <h1 className="text-3xl font-bold text-gray-800 leading-tight">
            みんなで決める<br />
            <span className="text-red-600">レストラン推薦</span>
          </h1>
          <p className="text-gray-600 text-lg leading-relaxed">
            AIが個別にヒアリングして、<br />
            グループ全員が満足できる<br />
            お店を見つけます
          </p>
        </div>

        {/* 特徴 */}
        <div className="bg-white rounded-2xl p-6 shadow-lg space-y-4">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">こんな時に便利</h2>
          <div className="grid gap-4 text-left">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                <span className="text-red-600 text-sm">👥</span>
              </div>
              <span className="text-gray-700">みんな遠慮して決まらない</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center">
                <span className="text-teal-600 text-sm">🤔</span>
              </div>
              <span className="text-gray-700">予算や好みがバラバラ</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <span className="text-yellow-600 text-sm">⏰</span>
              </div>
              <span className="text-gray-700">効率的に決めたい</span>
            </div>
          </div>
        </div>

        {/* 使い方 */}
        <div className="bg-gradient-to-r from-red-50 to-teal-50 rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">使い方</h2>
          <div className="space-y-3 text-sm text-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold">1</div>
              <span>グループを作成または参加</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold">2</div>
              <span>AIと個別に好みをチャット</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold">3</div>
              <span>おすすめのお店が提案される</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold">4</div>
              <span>みんなで投票して決定</span>
            </div>
          </div>
        </div>

        {/* アクションボタン */}
        <div className="space-y-4">
          <Link to="/user/create?action=create">
            <Button size="lg" className="w-full">
              グループを作成
            </Button>
          </Link>
          <Link to="/user/create?action=join">
            <Button variant="secondary" size="lg" className="w-full">
              グループに参加
            </Button>
          </Link>
        </div>

        {/* フッター */}
        <div className="text-xs text-gray-500 space-y-2 pt-8">
          <p>2〜6人のグループに対応</p>
          <p>匿名で安心してご利用いただけます</p>
        </div>
      </div>
    </Layout>
  );
};