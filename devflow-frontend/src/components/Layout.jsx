import { useEffect, useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { listNotifications } from '../api/notifications';

const navLinkClasses = ({ isActive }) =>
  `px-3 py-2 rounded text-sm font-medium transition ${
    isActive
      ? 'bg-gray-800 text-white'
      : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
  }`;

const Layout = () => {
  const { user, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  const refreshUnreadCount = () => {
    // Pagination gives an exact count without needing to fetch the actual
    // notification objects -- cheap enough to call after any action that
    // might change unread state (marking read, mount, etc.).
    listNotifications({ is_read: false })
      .then((res) => setUnreadCount(res.data.count))
      .catch(() => {
        // Non-critical -- badge just stays at its last known value.
      });
  };

  useEffect(() => {
    refreshUnreadCount();
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <span className="text-xl font-bold text-indigo-400">DevFlow</span>

            <nav className="flex items-center gap-1">
              <NavLink to="/" end className={navLinkClasses}>
                Dashboard
              </NavLink>
              <NavLink to="/projects" className={navLinkClasses}>
                Projects
              </NavLink>
              <NavLink to="/notifications" className={navLinkClasses}>
                <span className="inline-flex items-center gap-1.5">
                  Notifications
                  {unreadCount > 0 && (
                    <span className="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1 rounded-full bg-indigo-500 text-white text-xs font-semibold">
                      {unreadCount > 99 ? '99+' : unreadCount}
                    </span>
                  )}
                </span>
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
        <Outlet context={{ refreshUnreadCount }} />
      </main>
    </div>
  );
};

export default Layout;