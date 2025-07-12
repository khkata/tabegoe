import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// Pages
import { Landing } from './pages/Landing';
import { UserCreate } from './pages/UserCreate';
import { GroupCreate } from './pages/GroupCreate';
import { GroupJoin } from './pages/GroupJoin';
import { GroupLobby } from './pages/GroupLobby';
import { Interview } from './pages/Interview';
import { Waiting } from './pages/Waiting';
import { Recommendations } from './pages/Recommendations';
import { Vote } from './pages/Vote';
import { Result } from './pages/Result';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/user/create" element={<UserCreate />} />
            <Route path="/group/create" element={<GroupCreate />} />
            <Route path="/group/join" element={<GroupJoin />} />
            <Route path="/group/:groupId/lobby" element={<GroupLobby />} />
            <Route path="/group/:groupId/interview" element={<Interview />} />
            <Route path="/group/:groupId/waiting" element={<Waiting />} />
            <Route path="/group/:groupId/recommendations" element={<Recommendations />} />
            <Route path="/group/:groupId/vote" element={<Vote />} />
            <Route path="/group/:groupId/result" element={<Result />} />
          </Routes>
          
          <Toaster
            position="top-center"
            toastOptions={{
              duration: 3000,
              style: {
                background: '#363636',
                color: '#fff',
                borderRadius: '12px',
                padding: '12px 16px',
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;