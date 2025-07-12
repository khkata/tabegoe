import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Layout } from '../components/Layout/Layout';
import { Button } from '../components/UI/Button';
import { LoadingSpinner } from '../components/UI/LoadingSpinner';
import { interviewApi } from '../services/api';
import { useStore } from '../store/useStore';
import { InterviewMessage } from '../types';

export const Interview: React.FC = () => {
  const navigate = useNavigate();
  const { groupId } = useParams<{ groupId: string }>();
  const { currentUser, currentGroup, currentInterview, setCurrentInterview } = useStore();
  const [messages, setMessages] = useState<InterviewMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!groupId || !currentUser || !currentGroup) {
      navigate('/');
      return;
    }

    const startOrResumeInterview = async () => {
      setIsLoading(true);
      try {
        console.log('Starting/resuming interview for:', currentUser.user_id, 'in group:', groupId);
        const interview = await interviewApi.startInterview(groupId, currentUser.user_id);
        console.log('Interview data received:', interview);
        
        setCurrentInterview(interview);
        setMessages(interview.messages || []);
        
        if (interview.messages && interview.messages.length > 0) {
          console.log('Resumed existing interview with', interview.messages.length, 'messages');
        } else {
          console.log('Started new interview');
        }
      } catch (error: any) {
        console.error('Interview start/resume error:', error);
        if (error.response?.status === 400) {
          console.log('400 error details:', error.response.data);
        }
        toast.error('ヒアリングの開始に失敗しました');
        navigate(`/group/${groupId}/lobby?userId=${currentUser.user_id}`);
      } finally {
        setIsLoading(false);
      }
    };

    if (!currentInterview || currentInterview.group_id !== groupId) {
      startOrResumeInterview();
    } else {
      setMessages(currentInterview.messages || []);
    }
  }, [groupId, currentUser, currentGroup, currentInterview, navigate, setCurrentInterview]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentInterview || isSending) return;

    const userMessage = inputMessage;
    setInputMessage('');
    setIsSending(true);

    // ユーザーメッセージを即座に表示
    const tempUserMessage: InterviewMessage = {
      message_id: 'temp-user',
      interview_id: currentInterview.interview_id,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      const response = await interviewApi.sendMessage(currentInterview.interview_id, {
        message: userMessage,
      });
      
      // 一時メッセージを削除して実際のレスポンスを追加
      setMessages(prev => prev.filter(msg => msg.message_id !== 'temp-user'));
      setMessages(prev => [...prev, response]);
    } catch (error) {
      setMessages(prev => prev.filter(msg => msg.message_id !== 'temp-user'));
      toast.error('メッセージの送信に失敗しました');
    } finally {
      setIsSending(false);
    }
  };

  const completeInterview = async () => {
    if (!currentInterview) return;

    setIsLoading(true);
    try {
      await interviewApi.completeInterview(currentInterview.interview_id);
      toast.success('ヒアリングが完了しました！ロビーに戻ります');
      // ヒアリング完了後は必ずロビーに戻る
      const userParam = currentUser?.user_id ? `?userId=${currentUser.user_id}` : '';
      navigate(`/group/${groupId}/lobby${userParam}`);
    } catch (error) {
      toast.error('ヒアリング完了の処理に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout className="flex flex-col h-screen">
      <div className="flex-1 flex flex-col space-y-4">
        {/* ヘッダー */}
        <div className="text-center space-y-2 bg-white rounded-2xl p-4 shadow-lg">
          <div className="text-3xl">🤖</div>
          <h1 className="text-xl font-bold text-gray-800">AIヒアリング</h1>
          <p className="text-sm text-gray-600">
            {currentUser?.nickname}さんの好みをお聞かせください
          </p>
        </div>

        {/* チャットエリア */}
        <div className="flex-1 bg-white rounded-2xl shadow-lg flex flex-col min-h-0">
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <p>AIからの質問をお待ちください...</p>
              </div>
            )}
            
            {messages.map((message, index) => (
              <div
                key={`${message.message_id}-${index}`}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-red-500 to-red-600 text-white'
                      : 'bg-gray-100 text-gray-800 border'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm">🤖</span>
                      <span className="text-xs font-medium text-gray-600">AI</span>
                    </div>
                  )}
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>
              </div>
            ))}
            
            {isSending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 px-4 py-3 rounded-2xl border">
                  <div className="flex items-center space-x-2">
                    <LoadingSpinner size="sm" />
                    <span className="text-sm text-gray-600">AIが考え中...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* 入力エリア */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="メッセージを入力..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                rows={1}
                disabled={isSending}
              />
              <Button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isSending}
                className="px-6"
              >
                送信
              </Button>
            </div>
          </div>
        </div>

        {/* アクション */}
        <div className="space-y-3">
          <Button
            variant="secondary"
            size="lg"
            className="w-full"
            onClick={completeInterview}
            disabled={isLoading || messages.length === 0}
          >
            {isLoading ? <LoadingSpinner size="sm" /> : 'ヒアリング完了'}
          </Button>
          
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
      </div>
    </Layout>
  );
};