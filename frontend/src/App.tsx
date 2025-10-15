import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Studies } from './pages/Studies';
import { StudyDetail } from './pages/StudyDetail';
import { StudyDashboard } from './pages/StudyDashboard';
import { useAuthStore } from './store/authStore';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
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
    </BrowserRouter>
  );
}

export default App;
