import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { workoutsAPI, dietsAPI, progressAPI } from '../services/api';
import { 
  Dumbbell, 
  Apple, 
  TrendingUp, 
  Calendar,
  Target,
  Clock,
  Plus,
  Activity,
  BarChart3,
  Zap,
  Award
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalWorkouts: 0,
    totalDiets: 0,
    recentProgress: null,
    weeklyWorkouts: 0,
  });
  const [recentWorkouts, setRecentWorkouts] = useState([]);
  const [recentDiets, setRecentDiets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [progressData, setProgressData] = useState([]);
  const [weeklyActivity, setWeeklyActivity] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [workoutsRes, dietsRes, progressRes] = await Promise.all([
        workoutsAPI.getWorkouts(),
        dietsAPI.getDiets(),
        progressAPI.getProgress(),
      ]);

      const workouts = Array.isArray(workoutsRes.data) ? workoutsRes.data : workoutsRes.data.results || [];
      const diets = Array.isArray(dietsRes.data) ? dietsRes.data : dietsRes.data.results || [];
      const progress = Array.isArray(progressRes.data) ? progressRes.data : progressRes.data.results || [];

      setStats({
        totalWorkouts: workouts.length,
        totalDiets: diets.length,
        recentProgress: progress.length > 0 ? progress[0] : null,
        weeklyWorkouts: workouts.filter(w => {
          const weekAgo = new Date();
          weekAgo.setDate(weekAgo.getDate() - 7);
          return new Date(w.created_at) > weekAgo;
        }).length,
      });

      setRecentWorkouts(workouts.slice(0, 3));
      setRecentDiets(diets.slice(0, 3));
      
      // Dados de exemplo para gráficos (em produção, viriam da API)
      setProgressData([
        { date: '2024-01', weight: 75, muscle: 35 },
        { date: '2024-02', weight: 74, muscle: 36 },
        { date: '2024-03', weight: 73, muscle: 37 },
        { date: '2024-04', weight: 72, muscle: 38 },
      ]);
      
      setWeeklyActivity([
        { day: 'Seg', workouts: 1, calories: 300 },
        { day: 'Ter', workouts: 0, calories: 0 },
        { day: 'Qua', workouts: 1, calories: 450 },
        { day: 'Qui', workouts: 1, calories: 350 },
        { day: 'Sex', workouts: 0, calories: 0 },
        { day: 'Sáb', workouts: 1, calories: 500 },
        { day: 'Dom', workouts: 0, calories: 0 },
      ]);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (duration) => {
    if (!duration) return 'N/A';
    const match = duration.match(/(\d+):(\d+):(\d+)/);
    if (match) {
      const hours = parseInt(match[1]);
      const minutes = parseInt(match[2]);
      return hours > 0 ? `${hours}h ${minutes}min` : `${minutes}min`;
    }
    return duration;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-blue-600 text-white rounded-lg p-6 shadow-lg">
        <h1 className="text-3xl font-bold mb-2">
          Olá, {user?.first_name || 'Usuário'}! 👋
        </h1>
        <p className="text-blue-100 text-lg">
          Bem-vindo de volta ao seu painel de fitness. Vamos continuar sua jornada!
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total de Treinos</p>
              <p className="text-3xl font-bold text-gray-900">{stats.totalWorkouts}</p>
            </div>
            <div className="p-4 bg-blue-500 rounded-2xl shadow-lg">
              <Dumbbell className="h-8 w-8 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Dietas Criadas</p>
              <p className="text-3xl font-bold text-gray-900">{stats.totalDiets}</p>
            </div>
            <div className="p-4 bg-green-500 rounded-2xl shadow-lg">
              <Apple className="h-8 w-8 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Esta Semana</p>
              <p className="text-3xl font-bold text-gray-900">{stats.weeklyWorkouts}</p>
            </div>
            <div className="p-4 bg-purple-500 rounded-2xl shadow-lg">
              <Calendar className="h-8 w-8 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Peso Atual</p>
              <p className="text-3xl font-bold text-gray-900">
                {stats.recentProgress?.weight || user?.weight || '--'} kg
              </p>
            </div>
            <div className="p-4 bg-orange-500 rounded-2xl shadow-lg">
              <TrendingUp className="h-8 w-8 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/workouts/generate" className="bg-blue-600 text-white rounded-lg p-6 shadow-lg hover:bg-blue-700 transition-colors">
          <div className="flex items-center space-x-4">
            <div className="p-4 bg-white bg-opacity-20 rounded-2xl">
              <Plus className="h-8 w-8 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Gerar Treino</h3>
              <p className="text-blue-100">Crie um novo treino personalizado</p>
            </div>
          </div>
        </Link>

        <Link to="/diets/generate" className="bg-green-600 text-white rounded-lg p-6 shadow-lg hover:bg-green-700 transition-colors">
          <div className="flex items-center space-x-4">
            <div className="p-4 bg-white bg-opacity-20 rounded-2xl">
              <Plus className="h-8 w-8 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Gerar Dieta</h3>
              <p className="text-green-100">Crie um plano alimentar personalizado</p>
            </div>
          </div>
        </Link>

        <Link to="/progress" className="bg-purple-600 text-white rounded-lg p-6 shadow-lg hover:bg-purple-700 transition-colors">
          <div className="flex items-center space-x-4">
            <div className="p-4 bg-white bg-opacity-20 rounded-2xl">
              <TrendingUp className="h-8 w-8 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Registrar Progresso</h3>
              <p className="text-purple-100">Acompanhe sua evolução</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Progress Chart */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Progresso do Peso</h2>
            <BarChart3 className="h-6 w-6 text-blue-600" />
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={progressData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="weight" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Weekly Activity Chart */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Atividade Semanal</h2>
            <Activity className="h-6 w-6 text-green-600" />
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={weeklyActivity}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="workouts" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Workouts */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Treinos Recentes</h2>
            <Link to="/workouts" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              Ver todos
            </Link>
          </div>
          
          {recentWorkouts.length > 0 ? (
            <div className="space-y-3">
              {recentWorkouts.map((workout) => (
                <div key={workout.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="p-2 bg-blue-100 rounded-full">
                    <Dumbbell className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">
                      {workout.name || workout.workout_type}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {formatDuration(workout.duration)}
                      </span>
                      <span className="capitalize">{workout.intensity}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Dumbbell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">Nenhum treino encontrado</p>
              <Link to="/workouts/generate" className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Criar Primeiro Treino
              </Link>
            </div>
          )}
        </div>

        {/* Recent Diets */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Dietas Recentes</h2>
            <Link to="/diets" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              Ver todas
            </Link>
          </div>
          
          {recentDiets.length > 0 ? (
            <div className="space-y-3">
              {recentDiets.map((diet) => (
                <div key={diet.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="p-2 bg-green-100 rounded-full">
                    <Apple className="h-5 w-5 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">
                      {diet.name || `Dieta ${diet.goal}`}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>{diet.calories} kcal</span>
                      <span className="capitalize">{diet.goal}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Apple className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">Nenhuma dieta encontrada</p>
              <Link to="/diets/generate" className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                Criar Primeira Dieta
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;