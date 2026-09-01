import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';

// Temporary Dashboard Placeholder to verify authentication flow
const DashboardPlaceholder = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto flex items-center justify-between border-b border-gray-800 pb-6 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-indigo-400">DevFlow Dashboard</h1>
          <p className="mt-1 text-gray-400">
            Welcome back, <span className="text-white font-semibold">{user?.username}</span>!
          </p>
        </div>
        <button
          onClick={logout}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded transition"
        >
          Sign Out
        </button>
      </div>

      <div className="max-w-4xl mx-auto bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-lg font-semibold mb-2">Authentication Status</h2>
        <p className="text-green-400 font-mono text-sm">
          ✓ JWT tokens active & session successfully validated against /api/auth/me/
        </p>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Route */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<DashboardPlaceholder />} />
          </Route>

          {/* Fallback Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;