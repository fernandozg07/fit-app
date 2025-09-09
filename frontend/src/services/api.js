import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://web-production-567f4.up.railway.app';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para lidar com respostas e renovar token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/accounts/api/token/refresh/`, {
            refresh: refreshToken,
          });
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) =>
    api.post('/accounts/api/token/', { email, password }),
  
  register: (userData) =>
    api.post('/accounts/register/', userData),
  
  refreshToken: (refresh) =>
    api.post('/accounts/api/token/refresh/', { refresh }),
  
  getProfile: () =>
    api.get('/accounts/api/users/me/'),
  
  updateProfile: (userData) =>
    api.patch('/accounts/api/users/me/', userData),
};

// Workouts API
export const workoutsAPI = {
  getWorkouts: () =>
    api.get('/workouts/'),
  
  getWorkout: (id) =>
    api.get(`/workouts/${id}/`),
  
  generateWorkout: (preferences) =>
    api.post('/workouts/generate/', preferences),
  
  registerWorkout: (workoutData) =>
    api.post('/workouts/register/', workoutData),
  
  updateWorkout: (id, data) =>
    api.patch(`/workouts/${id}/`, data),
  
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
  
  registerDiet: (dietData) =>
    api.post('/diets/register/', dietData),
  
  updateDiet: (id, data) =>
    api.patch(`/diets/${id}/`, data),
  
  deleteDiet: (id) =>
    api.delete(`/diets/${id}/`),
};

// Progress API
export const progressAPI = {
  getProgress: () =>
    api.get('/progress/'),
  
  addProgress: (data) =>
    api.post('/progress/', data),
  
  updateProgress: (id, data) =>
    api.patch(`/progress/${id}/`, data),
  
  deleteProgress: (id) =>
    api.delete(`/progress/${id}/`),
};

// Chat API
export const chatAPI = {
  sendMessage: (message) =>
    api.post('/chat/', { user_message: message }),
  
  getChatHistory: () =>
    api.get('/chat/'),
};

export default api;