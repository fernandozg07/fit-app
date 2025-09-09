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
  Activity
} from 'lucide-react';

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
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getWorkoutTypeIcon = (type) => {
    switch (type) {
      case 'cardio':
        return <Activity className="h-5 w-5" />;
      case 'musculacao':
        return <Dumbbell className="h-5 w-5" />;
      default:
        return <Target className="h-5 w-5" />;
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
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          Olá, {user?.first_name || 'Usuário'}! 👋
        </h1>
        <p className="text-blue-100">
          Bem-vindo de volta ao seu painel de fitness. Vamos continuar sua jornada!
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total de Treinos</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalWorkouts}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Dumbbell className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Dietas Criadas</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalDiets}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <Apple className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Treinos esta Semana</p>
              <p className="text-2xl font-bold text-gray-900">{stats.weeklyWorkouts}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Peso Atual</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.recentProgress?.weight || user?.weight || '--'} kg
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <TrendingUp className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/workouts/generate"
          className="bg-white rounded-lg p-6 shadow-sm border hover:shadow-md transition-shadow group"
        >
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-blue-100 rounded-full group-hover:bg-blue-200 transition-colors">
              <Plus className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Gerar Treino</h3>
              <p className="text-sm text-gray-600">Crie um novo treino personalizado</p>
            </div>
          </div>
        </Link>

        <Link
          to="/diets/generate"
          className="bg-white rounded-lg p-6 shadow-sm border hover:shadow-md transition-shadow group"
        >
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-green-100 rounded-full group-hover:bg-green-200 transition-colors">
              <Plus className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Gerar Dieta</h3>
              <p className="text-sm text-gray-600">Crie um plano alimentar personalizado</p>
            </div>
          </div>
        </Link>

        <Link
          to="/progress"
          className="bg-white rounded-lg p-6 shadow-sm border hover:shadow-md transition-shadow group"
        >
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-purple-100 rounded-full group-hover:bg-purple-200 transition-colors">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Registrar Progresso</h3>
              <p className="text-sm text-gray-600">Acompanhe sua evolução</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Workouts */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Treinos Recentes</h2>
            <Link
              to="/workouts"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Ver todos
            </Link>
          </div>
          
          {recentWorkouts.length > 0 ? (
            <div className="space-y-3">
              {recentWorkouts.map((workout) => (
                <div key={workout.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="p-2 bg-blue-100 rounded-full">
                    {getWorkoutTypeIcon(workout.workout_type)}
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
            <p className="text-gray-500 text-center py-4">
              Nenhum treino encontrado. 
              <Link to="/workouts/generate" className="text-blue-600 hover:underline ml-1">
                Crie seu primeiro treino!
              </Link>
            </p>
          )}
        </div>

        {/* Recent Diets */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Dietas Recentes</h2>
            <Link
              to="/diets"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
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
            <p className="text-gray-500 text-center py-4">
              Nenhuma dieta encontrada. 
              <Link to="/diets/generate" className="text-blue-600 hover:underline ml-1">
                Crie sua primeira dieta!
              </Link>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;