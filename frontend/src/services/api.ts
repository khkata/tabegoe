import axios from 'axios';
import { 
  User, 
  Group, 
  Interview, 
  InterviewMessage, 
  Recommendation,
  CreateUserRequest,
  CreateGroupRequest,
  JoinGroupRequest,
  ChatMessageRequest 
} from '../types';

const API_BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// User API
export const userApi = {
  createAnonymousUser: async (data: CreateUserRequest): Promise<User> => {
    const response = await api.post('/users/anonymous', data);
    return response.data;
  },
  
  getUser: async (userId: string): Promise<User> => {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  },
};

// Group API
export const groupApi = {
  createGroup: async (data: CreateGroupRequest): Promise<Group> => {
    const response = await api.post('/groups/', data);
    return response.data;
  },
  
  joinGroup: async (data: JoinGroupRequest): Promise<Group> => {
    const response = await api.post('/groups/join', data);
    return response.data;
  },
  
  getGroup: async (groupId: string): Promise<Group> => {
    const response = await api.get(`/groups/${groupId}`);
    return response.data;
  },
};

// Interview API
export const interviewApi = {
  startInterview: async (groupId: string, userId: string): Promise<Interview> => {
    try {
      console.log(`Starting interview - Group: ${groupId}, User: ${userId}`);
      const response = await api.post(`/interviews/groups/${groupId}/users/${userId}/interviews`);
      console.log('Interview started successfully:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Interview start error:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      throw error;
    }
  },
  
  sendMessage: async (interviewId: string, data: ChatMessageRequest): Promise<InterviewMessage> => {
    const response = await api.post(`/interviews/${interviewId}/chat`, data);
    return response.data;
  },
  
  completeInterview: async (interviewId: string): Promise<Interview> => {
    const response = await api.post(`/interviews/${interviewId}/complete`);
    return response.data;
  },
  
  getInterview: async (interviewId: string): Promise<Interview> => {
    const response = await api.get(`/interviews/${interviewId}`);
    return response.data;
  },
  
  getGroupInterviewStatus: async (groupId: string): Promise<any> => {
    const response = await api.get(`/interviews/groups/${groupId}/interview-status`);
    return response.data;
  },
};

// Recommendation API
export const recommendationApi = {
  generateRecommendations: async (groupId: string): Promise<Recommendation> => {
    const response = await api.post(`/recommendations/groups/${groupId}/recommendations`);
    return response.data;
  },
  
  getRecommendations: async (groupId: string): Promise<Recommendation> => {
    const response = await api.get(`/recommendations/groups/${groupId}/recommendations`);
    return response.data;
  },
  
  getInterviewStatus: async (groupId: string): Promise<any> => {
    const response = await api.get(`/recommendations/groups/${groupId}/interview-status`);
    return response.data;
  },

  setFinalDecision: async (groupId: string, restaurantId: string, restaurantName: string, decidedByUserId: string): Promise<any> => {
    const response = await api.post(`/recommendations/groups/${groupId}/final-decision`, {
      restaurant_id: restaurantId,
      restaurant_name: restaurantName,
      decided_by_user_id: decidedByUserId
    });
    return response.data;
  },

  getFinalDecision: async (groupId: string): Promise<any> => {
    const response = await api.get(`/recommendations/groups/${groupId}/final-decision`);
    return response.data;
  },
};

// Vote API
export const voteApi = {
  voteForCandidate: async (candidateId: string, voteType: string, userId: string): Promise<any> => {
    console.log('voteApi.voteForCandidate called with:', { candidateId, voteType, userId });
    const url = `/recommendations/candidates/${candidateId}/vote`;
    console.log('Vote API URL:', API_BASE_URL + url);
    
    try {
      const response = await api.post(url, {
        vote_type: voteType,
        user_id: userId
      });
      console.log('Vote API response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Vote API error:', error);
      throw error;
    }
  },
  
  getGroupVotes: async (groupId: string): Promise<any> => {
    const response = await api.get(`/recommendations/groups/${groupId}/votes`);
    return response.data;
  },
  
  getUserVote: async (groupId: string, userId: string): Promise<any> => {
    const response = await api.get(`/recommendations/groups/${groupId}/user/${userId}/vote`);
    return response.data;
  },
};

export default api;