import { createContext } from 'react';

// Split into its own file (not exported alongside AuthProvider) so that
// AuthContext.jsx can export only a component, per Vite's Fast Refresh
// lint rule (react-refresh/only-export-components).
export const AuthContext = createContext(null);