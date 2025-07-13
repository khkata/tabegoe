export interface User {
  user_id: string;
  nickname: string;
  preferences?: string;
  created_at: string;
}

export interface Group {
  group_id: string;
  name: string;
  description?: string;
  invite_code: string;
  status: 'waiting' | 'interviewing' | 'recommending' | 'voting' | 'completed';
  host_user_id: string;
  members: User[];
  created_at: string;
}

export interface InterviewMessage {
  message_id: string;
  interview_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  is_mock?: boolean;  // AI応答がモックかどうか
  ai_source?: string;  // AI応答のソース（"openai" or "mock"）
  ai_model?: string;   // 使用されたAIモデル
}

export interface Interview {
  interview_id: string;
  group_id: string;
  user_id: string;
  status: 'pending' | 'completed';
  messages: InterviewMessage[];
  created_at: string;
}

export interface Restaurant {
  restaurant_id: string;
  name: string;
  cuisine_type: string;
  price_range: string;
  address: string;
  external_rating: number;
  external_review_count: number;
  image_url: string;
  vote_count: number;
}

export interface Recommendation {
  recommendation_id: string;
  group_id: string;
  reasoning: string;
  restaurants: Restaurant[];
  created_at: string;
}

export interface CreateUserRequest {
  nickname: string;
  preferences?: string;
}

export interface CreateGroupRequest {
  name: string;
  host_user_id: string;
  description?: string;
}

export interface JoinGroupRequest {
  invite_code: string;
  user_id: string;
}

export interface ChatMessageRequest {
  message: string;
}