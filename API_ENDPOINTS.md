# 🚀 API ENDPOINTS - FIT APP

## 🔐 **AUTENTICAÇÃO**

### Registro
```
POST /accounts/register/
Body: {
  "email": "user@example.com",
  "password": "senha123",
  "first_name": "Nome",
  "last_name": "Sobrenome"
}
Response: {
  "user": {...},
  "access_token": "...",
  "refresh_token": "..."
}
```

### Login
```
POST /accounts/token/
Body: {
  "email": "user@example.com",
  "password": "senha123"
}
Response: {
  "access": "...",
  "refresh": "..."
}
```

### Refresh Token
```
POST /accounts/token/refresh/
Body: {
  "refresh": "refresh_token_here"
}
```

## 👤 **USUÁRIO**

### Perfil do Usuário
```
GET /accounts/users/{id}/
Headers: Authorization: Bearer {access_token}
```

### Atualizar Perfil
```
PATCH /accounts/users/{id}/
Headers: Authorization: Bearer {access_token}
Body: {
  "weight": 70.5,
  "height": 175,
  "fitness_goal": "perda_peso"
}
```

## 🍎 **DIETAS**

### Listar Planos de Dieta
```
GET /diets/
Headers: Authorization: Bearer {access_token}
```

### Gerar Nova Dieta
```
POST /diets/generate/
Headers: Authorization: Bearer {access_token}
Body: {
  "goal": "perda_peso",
  "calories_target": 2000,
  "meals_count": 4,
  "dietary_restrictions": ["vegetariano"],
  "preferred_cuisine": "brasileira"
}
```

### Registrar Dieta Manual
```
POST /diets/register/
Headers: Authorization: Bearer {access_token}
Body: {
  "meal": "breakfast",
  "calories": 350,
  "protein": 20,
  "carbs": 45,
  "fat": 12
}
```

## 💪 **TREINOS**

### Listar Treinos
```
GET /workouts/
Headers: Authorization: Bearer {access_token}
```

### Gerar Novo Treino
```
POST /workouts/generate/
Headers: Authorization: Bearer {access_token}
Body: {
  "workout_type": "musculacao",
  "difficulty": "intermediario",
  "duration": 45,
  "muscle_groups": ["peito", "triceps"],
  "equipment": ["halteres", "banco"]
}
```

### Feedback de Treino
```
POST /workouts/{id}/feedback/
Headers: Authorization: Bearer {access_token}
Body: {
  "rating": 4,
  "comments": "Treino excelente!",
  "duration_minutes": 50,
  "exercise_logs": [...]
}
```

## 📊 **PROGRESSO**

### Listar Registros de Progresso
```
GET /progress/
Headers: Authorization: Bearer {access_token}
```

### Criar Registro de Progresso
```
POST /progress/
Headers: Authorization: Bearer {access_token}
Body: {
  "date": "2024-01-15",
  "weight": 70.5,
  "body_fat": 15.2,
  "muscle_mass": 55.3
}
```

### Estatísticas de Progresso
```
GET /progress/stats/
Headers: Authorization: Bearer {access_token}
```

### Exportar Progresso (CSV)
```
GET /progress/export/
Headers: Authorization: Bearer {access_token}
```

## 🤖 **CHATBOT**

### Chat com IA
```
POST /chat/
Headers: Authorization: Bearer {access_token}
Body: {
  "message": "Qual meu peso atual?"
}
Response: {
  "response": "Seu peso atual registrado é 70.5 kg..."
}
```

## 📚 **DOCUMENTAÇÃO**

### Swagger UI
```
GET /swagger/
```

### ReDoc
```
GET /redoc/
```

## 🔧 **CONFIGURAÇÃO FRONTEND**

### Base URL
```javascript
const API_BASE_URL = 'https://web-production-567f4.up.railway.app'
```

### Headers Padrão
```javascript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${accessToken}`
}
```

### Exemplo de Requisição
```javascript
// Login
const login = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/accounts/token/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  return response.json()
}

// Gerar Dieta
const generateDiet = async (dietData) => {
  const response = await fetch(`${API_BASE_URL}/diets/generate/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify(dietData)
  })
  return response.json()
}
```

## ✅ **STATUS DOS ENDPOINTS**

- ✅ Autenticação (Login/Register/Refresh)
- ✅ Perfil de Usuário (CRUD)
- ✅ Dietas (Gerar/Listar/Registrar)
- ✅ Treinos (Gerar/Listar/Feedback)
- ✅ Progresso (CRUD/Stats/Export)
- ✅ Chatbot (IA Personalizada)
- ✅ Documentação (Swagger/ReDoc)

**🎯 TODOS OS ENDPOINTS ESTÃO FUNCIONAIS!**