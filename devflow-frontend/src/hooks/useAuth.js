import { useContext } from 'react';
import { AuthContext } from '../context/authContextObject';

export const useAuth = () => useContext(AuthContext);