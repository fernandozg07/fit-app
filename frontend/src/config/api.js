// Frontend API Configuration
export const API_CONFIG = {
  BASE_URL: 'https://web-production-567f4.up.railway.app',
  ENDPOINTS: {
    // Auth
    REGISTER: '/accounts/register/',
    LOGIN: '/accounts/token/',
    REFRESH: '/accounts/token/refresh/',
    
    // User
    USER_PROFILE: '/accounts/users/',
    
    // Diets
    DIETS: '/diets/',
    GENERATE_DIET: '/diets/generate/',
    REGISTER_DIET: '/diets/register/',
    
    // Workouts
    WORKOUTS: '/workouts/',
    GENERATE_WORKOUT: '/workouts/generate/',
    REGISTER_WORKOUT: '/workouts/register/',
    WORKOUT_FEEDBACK: (id) => `/workouts/${id}/feedback/`,
    
    // Progress
    PROGRESS: '/progress/',
    PROGRESS_STATS: '/progress/stats/',
    PROGRESS_EXPORT: '/progress/export/',
    
    // Chat
    CHAT: '/chat/',
  }
}

// Helper function to get auth headers
export const getAuthHeaders = (token) => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`
})

// Helper function to make API calls
export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    }
  }
  
  const response = await fetch(url, { ...defaultOptions, ...options })
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`)
  }
  
  return response.json()
}