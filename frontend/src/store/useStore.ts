import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { User, Group, Interview, Recommendation } from '../types';

interface AppState {
  // User state
  currentUser: User | null;
  setCurrentUser: (user: User | null) => void;
  
  // Group state
  currentGroup: Group | null;
  setCurrentGroup: (group: Group | null) => void;
  
  // Interview state
  currentInterview: Interview | null;
  setCurrentInterview: (interview: Interview | null) => void;
  
  // Recommendation state
  currentRecommendation: Recommendation | null;
  setCurrentRecommendation: (recommendation: Recommendation | null) => void;
  
  // UI state
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  
  // Reset function
  reset: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // User state
      currentUser: null,
      setCurrentUser: (user) => set({ currentUser: user }),
      
      // Group state
      currentGroup: null,
      setCurrentGroup: (group) => set({ currentGroup: group }),
      
      // Interview state
      currentInterview: null,
      setCurrentInterview: (interview) => set({ currentInterview: interview }),
      
      // Recommendation state
      currentRecommendation: null,
      setCurrentRecommendation: (recommendation) => set({ currentRecommendation: recommendation }),
      
      // UI state
      isLoading: false,
      setIsLoading: (loading) => set({ isLoading: loading }),
      
      // Reset function
      reset: () => set({
        currentUser: null,
        currentGroup: null,
        currentInterview: null,
        currentRecommendation: null,
        isLoading: false,
      }),
    }),
    {
      name: 'carechoice-storage', // unique name for localStorage key
      storage: createJSONStorage(() => localStorage),
      // 永続化しないフィールドを指定
      partialize: (state) => ({
        currentUser: state.currentUser,
        currentGroup: state.currentGroup,
        currentInterview: state.currentInterview,
        currentRecommendation: state.currentRecommendation,
        // isLoadingは永続化しない
      }),
    }
  )
);