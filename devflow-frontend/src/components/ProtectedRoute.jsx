import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = () => {
  const { token, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
        <p className="text-lg animate-pulse">Loading DevFlow...</p>
      </div>
    );
  }

  return token ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;