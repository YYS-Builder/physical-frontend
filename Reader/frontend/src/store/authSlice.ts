import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

interface AuthState {
  isAuthenticated: boolean;
  user: {
    id: string;
    email: string;
  } | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  loading: false,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    loginSuccess: (state, action: PayloadAction<{ user: AuthState['user']; token: string }>) => {
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.loading = false;
      state.error = null;
    },
    loginFailure: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.loading = false;
      state.error = null;
    },
  },
});

export const { loginStart, loginSuccess, loginFailure, logout } = authSlice.actions;

export const login = (email: string, password: string) => async (dispatch: any) => {
  try {
    dispatch(loginStart());
    const response = await axios.post('/api/v1/token', {
      username: email,
      password,
    });
    const { access_token } = response.data;
    const userResponse = await axios.get('/api/v1/users/me', {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    dispatch(loginSuccess({ user: userResponse.data, token: access_token }));
  } catch (error: any) {
    dispatch(loginFailure(error.response?.data?.detail || 'Login failed'));
  }
};

export const register = (email: string, password: string) => async (dispatch: any) => {
  try {
    dispatch(loginStart());
    await axios.post('/api/v1/users/', {
      email,
      password,
    });
    dispatch(login(email, password));
  } catch (error: any) {
    dispatch(loginFailure(error.response?.data?.detail || 'Registration failed'));
  }
};

export default authSlice.reducer; 