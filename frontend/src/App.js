import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Workouts from './pages/Workouts';
import GenerateWorkout from './pages/GenerateWorkout';
import Diets from './pages/Diets';
import GenerateDiet from './pages/GenerateDiet';
import Progress from './pages/Progress';
import Chat from './pages/Chat';
import WorkoutDetail from './pages/WorkoutDetail';
import DietDetail from './pages/DietDetail';

// Componente para proteger rotas
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Componente para redirecionar usuários autenticados
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return !isAuthenticated ? children : <Navigate to="/dashboard" />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Rotas públicas */}
            <Route 
              path="/login" 
              element={
                <PublicRoute>
                  <Login />
                </PublicRoute>
              } 
            />
            <Route 
              path="/register" 
              element={
                <PublicRoute>
                  <Register />
                </PublicRoute>
              } 
            />
            
            {/* Rotas protegidas */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/workouts" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Workouts />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/workouts/generate" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <GenerateWorkout />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/workouts/:id" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <WorkoutDetail />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/diets" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Diets />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/diets/generate" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <GenerateDiet />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/diets/:id" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <DietDetail />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/progress" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Progress />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/chat" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Chat />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            
            {/* Rota padrão */}
            <Route path="/" element={<Navigate to="/dashboard" />} />
            
            {/* Rota 404 */}
            <Route 
              path="*" 
              element={
                <div className="min-h-screen flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                    <p className="text-gray-600 mb-4">Página não encontrada</p>
                    <a href="/dashboard" className="text-blue-600 hover:underline">
                      Voltar ao Dashboard
                    </a>
                  </div>
                </div>
              } 
            />
          </Routes>
          
          {/* Toast notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                theme: {
                  primary: '#4aed88',
                },
              },
            }}
          />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;