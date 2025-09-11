import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { workoutsAPI, dietsAPI, progressAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Dumbbell, 
  Apple, 
  TrendingUp, 
  Calendar,
  Target,
  Clock,
  Plus,
  Activity,
  Fire,
  Award,
  Zap
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
      <Card className="bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 text-white border-0 shadow-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Olá, {user?.first_name || 'Usuário'}! 👋
            </h1>
            <p className="text-blue-100 text-lg">
              Bem-vindo de volta ao seu painel de fitness. Vamos continuar sua jornada!
            </p>
            <div className="flex items-center mt-4 space-x-4">
              <div className="flex items-center text-yellow-300">
                <Fire className="h-5 w-5 mr-1" />
                <span className="font-semibold">{stats.weeklyWorkouts} treinos esta semana</span>
              </div>
              <div className="flex items-center text-green-300">
                <Award className="h-5 w-5 mr-1" />
                <span className="font-semibold">Nível: {stats.totalWorkouts > 10 ? 'Avançado' : stats.totalWorkouts > 5 ? 'Intermediário' : 'Iniciante'}</span>
              </div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="text-6xl opacity-20">💪</div>
          </div>
        </div>
      </Card>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card hover className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-700">Total de Treinos</p>
              <p className="text-3xl font-bold text-blue-900">{stats.totalWorkouts}</p>
              <p className="text-xs text-blue-600 mt-1">+{stats.weeklyWorkouts} esta semana</p>
            </div>
            <div className="p-4 bg-blue-500 rounded-2xl shadow-lg">
              <Dumbbell className="h-8 w-8 text-white" />
            </div>
          </div>
        </Card>

        <Card hover className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-700">Dietas Criadas</p>
              <p className="text-3xl font-bold text-green-900">{stats.totalDiets}</p>
              <p className="text-xs text-green-600 mt-1">Planos ativos</p>
            </div>
            <div className="p-4 bg-green-500 rounded-2xl shadow-lg">
              <Apple className="h-8 w-8 text-white" />
            </div>
          </div>
        </Card>

        <Card hover className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-700">Sequência</p>
              <p className="text-3xl font-bold text-purple-900">{stats.weeklyWorkouts}</p>
              <p className="text-xs text-purple-600 mt-1">dias seguidos</p>
            </div>
            <div className="p-4 bg-purple-500 rounded-2xl shadow-lg">
              <Zap className="h-8 w-8 text-white" />
            </div>
          </div>
        </Card>

        <Card hover className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-700">Peso Atual</p>
              <p className="text-3xl font-bold text-orange-900">
                {stats.recentProgress?.weight || user?.weight || '--'} kg
              </p>
              <p className="text-xs text-orange-600 mt-1">Meta: {user?.weight ? (user.weight - 5) : '--'} kg</p>
            </div>
            <div className="p-4 bg-orange-500 rounded-2xl shadow-lg">
              <TrendingUp className="h-8 w-8 text-white" />
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/workouts/generate">
          <Card hover className="group bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-xl">
            <div className="flex items-center space-x-4">
              <div className="p-4 bg-white bg-opacity-20 rounded-2xl group-hover:bg-opacity-30 transition-all">
                <Plus className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Gerar Treino</h3>
                <p className="text-blue-100">Crie um novo treino personalizado</p>
              </div>
            </div>
          </Card>
        </Link>

        <Link to="/diets/generate">
          <Card hover className="group bg-gradient-to-br from-green-500 to-green-600 text-white border-0 shadow-xl">
            <div className="flex items-center space-x-4">
              <div className="p-4 bg-white bg-opacity-20 rounded-2xl group-hover:bg-opacity-30 transition-all">
                <Plus className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Gerar Dieta</h3>
                <p className="text-green-100">Crie um plano alimentar personalizado</p>
              </div>
            </div>
          </Card>
        </Link>

        <Link to="/progress">
          <Card hover className="group bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-xl">
            <div className="flex items-center space-x-4">
              <div className="p-4 bg-white bg-opacity-20 rounded-2xl group-hover:bg-opacity-30 transition-all">
                <TrendingUp className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Registrar Progresso</h3>
                <p className="text-purple-100">Acompanhe sua evolução</p>
              </div>
            </div>
          </Card>
        </Link>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Workouts */}
        <Card>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Treinos Recentes</h2>
            <Link
              to="/workouts"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
            >
              Ver todos
              <Activity className="h-4 w-4 ml-1" />
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
            <div className="text-center py-8">
              <Dumbbell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">Nenhum treino encontrado</p>
              <Button as={Link} to="/workouts/generate" size="sm">
                Criar Primeiro Treino
              </Button>
            </div>
          )}
        </Card>

        {/* Recent Diets */}
        <Card>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Dietas Recentes</h2>
            <Link
              to="/diets"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
            >
              Ver todas
              <Apple className="h-4 w-4 ml-1" />
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
              <Button as={Link} to="/diets/generate" size="sm" variant="success">
                Criar Primeira Dieta
              </Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;