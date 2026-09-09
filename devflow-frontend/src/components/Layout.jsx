import { useEffect, useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { listNotifications } from '../api/notifications';

const navLinkClasses = ({ isActive }) =>
  `px-3 py-2 rounded text-sm font-medium transition ${
    isActive
      ? 'bg-gray-800 text-white'
      : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
  }`;

const mobileNavLinkClasses = ({ isActive }) =>
  `block px-3 py-2 rounded text-sm font-medium transition ${
    isActive
      ? 'bg-gray-800 text-white'
      : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
  }`;

const NotificationsLabel = ({ unreadCount }) => (
  <span className="inline-flex items-center gap-1.5">
    Notifications
    {unreadCount > 0 && (
      <span className="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1 rounded-full bg-indigo-500 text-white text-xs font-semibold">
        {unreadCount > 99 ? '99+' : unreadCount}
      </span>
    )}
  </span>
);

const Layout = () => {
  const { user, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <span className="text-xl font-bold text-indigo-400">DevFlow</span>

            {/* Desktop nav -- hidden below md, where it's replaced by the hamburger menu */}
            <nav className="hidden md:flex items-center gap-1">
              <NavLink to="/" end className={navLinkClasses}>
                Dashboard
              </NavLink>
              <NavLink to="/projects" className={navLinkClasses}>
                Projects
              </NavLink>
              <NavLink to="/notifications" className={navLinkClasses}>
                <NotificationsLabel unreadCount={unreadCount} />
              </NavLink>
            </nav>
          </div>

          {/* Desktop user info -- hidden below md */}
          <div className="hidden md:flex items-center gap-4">
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

          {/* Mobile hamburger toggle -- hidden at md and above */}
          <button
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            className="md:hidden p-2 text-gray-300 hover:text-white"
            aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
          >
            {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>

        {/* Mobile menu panel */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-800 px-4 py-3 space-y-1">
            <NavLink to="/" end className={mobileNavLinkClasses} onClick={() => setMobileMenuOpen(false)}>
              Dashboard
            </NavLink>
            <NavLink to="/projects" className={mobileNavLinkClasses} onClick={() => setMobileMenuOpen(false)}>
              Projects
            </NavLink>
            <NavLink
              to="/notifications"
              className={mobileNavLinkClasses}
              onClick={() => setMobileMenuOpen(false)}
            >
              <NotificationsLabel unreadCount={unreadCount} />
            </NavLink>

            <div className="pt-3 mt-2 border-t border-gray-800 flex items-center justify-between">
              <span className="text-sm text-gray-400">
                Signed in as <span className="text-white font-medium">{user?.username}</span>
              </span>
              <button
                onClick={logout}
                className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded transition"
              >
                Sign Out
              </button>
            </div>
          </div>
        )}
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <Outlet context={{ refreshUnreadCount }} />
      </main>
    </div>
  );
};

export default Layout;