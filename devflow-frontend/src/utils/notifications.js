// Notification.target_url on the backend points at the API path
// (e.g. "/api/projects/5/"), not a frontend route -- there is no
// "/api/..." page in this SPA. Translate the known patterns into the
// actual routes; anything unrecognized returns null (renders as plain text).
export const resolveNotificationLink = (targetUrl) => {
  if (!targetUrl) return null;
  const projectMatch = targetUrl.match(/\/api\/projects\/(\d+)\/?$/);
  if (projectMatch) return `/projects/${projectMatch[1]}`;
  const taskMatch = targetUrl.match(/\/api\/tasks\/(\d+)\/?$/);
  if (taskMatch) return `/tasks/${taskMatch[1]}`;
  return null;
};