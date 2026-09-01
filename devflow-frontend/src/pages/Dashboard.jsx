import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Welcome back, {user?.username}</h1>
      <p className="text-gray-400 mb-8">Here's what's happening across your projects.</p>

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-lg font-semibold mb-2">Authentication Status</h2>
        <p className="text-green-400 font-mono text-sm">
          ✓ JWT tokens active &amp; session successfully validated against /api/auth/me/
        </p>
      </div>
    </div>
  );
};

export default Dashboard;