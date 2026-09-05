import { useEffect, useState } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import { listNotifications, markNotificationRead, markAllNotificationsRead } from '../api/notifications';
import { resolveNotificationLink } from '../utils/notifications';
import { getErrorMessage } from '../utils/errors';

const Notifications = () => {
  const { refreshUnreadCount } = useOutletContext();

  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const [markingAll, setMarkingAll] = useState(false);

  useEffect(() => {
    let ignore = false;

    const load = async () => {
      try {
        const response = await listNotifications();
        if (ignore) return;
        setNotifications(response.data.results);
        setError('');
      } catch (err) {
        if (ignore) return;
        setError(getErrorMessage(err, 'Could not load notifications.'));
      } finally {
        if (!ignore) setLoading(false);
      }
    };

    load();
    return () => {
      ignore = true;
    };
  }, [refreshKey]);

  const handleNotificationClick = async (notification) => {
    if (!notification.is_read) {
      try {
        await markNotificationRead(notification.id);
        setRefreshKey((key) => key + 1);
        refreshUnreadCount();
      } catch {
        // Non-critical -- the person can still navigate even if marking-read failed.
      }
    }
  };

  const handleMarkAllRead = async () => {
    setMarkingAll(true);
    try {
      await markAllNotificationsRead();
      setRefreshKey((key) => key + 1);
      refreshUnreadCount();
    } catch (err) {
      setError(getErrorMessage(err, 'Could not mark all as read.'));
    } finally {
      setMarkingAll(false);
    }
  };

  const hasUnread = notifications.some((n) => !n.is_read);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Notifications</h1>
        {hasUnread && (
          <button
            onClick={handleMarkAllRead}
            disabled={markingAll}
            className="text-sm text-indigo-400 hover:text-indigo-300 disabled:opacity-50"
          >
            {markingAll ? 'Marking...' : 'Mark all as read'}
          </button>
        )}
      </div>

      {loading && <p className="text-gray-400">Loading notifications...</p>}

      {!loading && error && (
        <div className="p-3 bg-red-500/10 border border-red-500 text-red-400 text-sm rounded">
          {error}
        </div>
      )}

      {!loading && !error && notifications.length === 0 && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-8 text-center text-gray-400">
          No notifications yet.
        </div>
      )}

      {!loading && !error && notifications.length > 0 && (
        <ul className="space-y-2">
          {notifications.map((notification) => {
            const link = resolveNotificationLink(notification.target_url);
            const content = (
              <div
                className={`px-4 py-3 rounded border ${
                  notification.is_read
                    ? 'bg-gray-800 border-gray-700'
                    : 'bg-gray-800 border-indigo-500/50'
                }`}
              >
                <p className="text-sm">
                  <span className="font-medium">{notification.actor?.username}</span>{' '}
                  <span className="text-gray-300">{notification.verb}</span>
                </p>
                <div className="flex items-center gap-2 mt-1">
                  {!notification.is_read && (
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                  )}
                  <span className="text-xs text-gray-500">
                    {new Date(notification.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            );

            return (
              <li key={notification.id} onClick={() => handleNotificationClick(notification)}>
                {link ? (
                  <Link to={link} className="block">
                    {content}
                  </Link>
                ) : (
                  <div className="cursor-default">{content}</div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default Notifications;