// The API doesn't use one consistent key for single-message errors --
// custom actions return {"error": "..."} or {"message": "..."}, while
// some auth endpoints use {"detail": "..."}. This checks all three so
// callers don't have to know which one a given endpoint uses.
export const getErrorMessage = (err, fallback = 'Something went wrong. Please try again.') => {
  const data = err?.response?.data;
  if (!data || typeof data !== 'object') return fallback;
  return data.error || data.message || data.detail || fallback;
};