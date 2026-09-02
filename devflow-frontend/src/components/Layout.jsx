import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navLinkClasses = ({ isActive }) =>
  `px-3 py-2 rounded text-sm font-medium transition ${
    isActive
      ? 'bg-gray-800 text-white'
      : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
  }`;

const Layout = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <span className="text-xl font-bold text-indigo-400">DevFlow</span>

            {/* Nav links grow here as more sections ship (Notifications, ...) */}
            <nav className="flex items-center gap-1">
              <NavLink to="/" end className={navLinkClasses}>
                Dashboard
              </NavLink>
              <NavLink to="/projects" className={navLinkClasses}>
                Projects
              </NavLink>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">
              Signed in as <span className="text-white font-medium">{user?.username}</span>
            </span>
            <button
              onClick={logout}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded transition"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;