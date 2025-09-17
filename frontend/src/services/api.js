import axios from 'axios';

const API_BASE_URL = 'https://web-production-567f4.up.railway.app';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth API
export const authAPI = {
  login: (email, password) =>
    api.post('/accounts/token/', { email, password }),
  
  register: (userData) =>
    api.post('/accounts/register/', userData),
  
  getProfile: () =>
    api.get('/accounts/users/'),
};

// Workouts API
export const workoutsAPI = {
  getWorkouts: () =>
    api.get('/workouts/'),
  
  getWorkout: (id) =>
    api.get(`/workouts/${id}/`),
  
  generateWorkout: (preferences) =>
    api.post('/workouts/generate/', preferences),
  
  deleteWorkout: (id) =>
    api.delete(`/workouts/${id}/`),
  
  sendFeedback: (id, feedback) =>
    api.post(`/workouts/${id}/feedback/`, feedback),
};

// Diets API
export const dietsAPI = {
  getDiets: () =>
    api.get('/diets/'),
  
  getDiet: (id) =>
    api.get(`/diets/${id}/`),
  
  generateDiet: (preferences) =>
    api.post('/diets/generate/', preferences),
  
  deleteDiet: (id) =>
    api.delete(`/diets/${id}/`),
};

// Progress API
export const progressAPI = {
  getProgress: () =>
    api.get('/progress/'),
  
  addProgress: (data) =>
    api.post('/progress/', data),
  
  deleteProgress: (id) =>
    api.delete(`/progress/${id}/`),
};

// Chat API
export const chatAPI = {
  sendMessage: (message) =>
    api.post('/chat/', { message: message }),
  
  getChatHistory: () =>
    api.get('/chat/'),
};

export default api;