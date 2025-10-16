import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Suspense } from 'react';
import { useAuthStore } from './store/authStore';
import LoadingSpinner from './components/LoadingSpinner';

// Import all lazy-loaded components from centralized file
import {
  Login,
  Studies,
  StudyDetail,
  StudyDashboard
} from './lazyComponents';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/studies"
            element={
              <ProtectedRoute>
                <Studies />
              </ProtectedRoute>
            }
          />
          <Route
            path="/studies/:studyId/dashboard"
            element={
              <ProtectedRoute>
                <StudyDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/studies/:studyId"
            element={
              <ProtectedRoute>
                <StudyDetail />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
