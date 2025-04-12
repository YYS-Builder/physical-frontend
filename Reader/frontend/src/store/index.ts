import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import collectionsReducer from './collectionsSlice';
import documentsReducer from './documentsSlice';
import analyticsReducer from './analyticsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    collections: collectionsReducer,
    documents: documentsReducer,
    analytics: analyticsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 