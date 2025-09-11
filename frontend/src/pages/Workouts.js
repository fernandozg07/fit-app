import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { workoutsAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import useAsync from '../hooks/useAsync';
import { 
  Dumbbell, 
  Plus, 
  Clock, 
  Target, 
  Star,
  Trash2,
  Edit,
  Play,
  Filter,
  Search,
  SortAsc
} from 'lucide-react';
import toast from 'react-hot-toast';

const Workouts = () => {
  const [workouts, setWorkouts] = useState([]);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const { loading, execute } = useAsync();

  useEffect(() => {
    loadWorkouts();
  }, []);

  const loadWorkouts = async () => {
    await execute(async () => {
      const response = await workoutsAPI.getWorkouts();
      setWorkouts(Array.isArray(response.data) ? response.data : response.data.results || []);
    });
  };

  const handleDeleteWorkout = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir este treino?')) {
      try {
        await workoutsAPI.deleteWorkout(id);
        setWorkouts(workouts.filter(w => w.id !== id));
        toast.success('Treino excluído com sucesso!');
      } catch (error) {
        toast.error('Erro ao excluir treino');
      }
    }
  };

  const getWorkoutTypeIcon = (type) => {
    switch (type) {
      case 'cardio':
        return '🏃‍♂️';
      case 'musculacao':
        return '💪';
      case 'yoga':
        return '🧘‍♀️';
      case 'hiit':
        return '⚡';
      default:
        return '🎯';
    }
  };

  const getIntensityColor = (intensity) => {
    switch (intensity) {
      case 'baixa':
        return 'bg-green-100 text-green-800';
      case 'moderada':
        return 'bg-yellow-100 text-yellow-800';
      case 'alta':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
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

  const filteredWorkouts = workouts
    .filter(workout => {
      const matchesFilter = filter === 'all' || workout.workout_type === filter;
      const matchesSearch = !searchTerm || 
        workout.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        workout.workout_type?.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesFilter && matchesSearch;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return (a.name || a.workout_type).localeCompare(b.name || b.workout_type);
        case 'intensity':
          const intensityOrder = { 'baixa': 1, 'moderada': 2, 'alta': 3 };
          return intensityOrder[a.intensity] - intensityOrder[b.intensity];
        case 'created_at':
        default:
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });

  const workoutTypes = [...new Set(workouts.map(w => w.workout_type))];

  if (loading) {
    return <LoadingSpinner text="Carregando treinos..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 mb-8">
        <div className="animate-fade-in-up">
          <h1 className="text-4xl font-bold gradient-text mb-2">Meus Treinos</h1>
          <p className="text-gray-600 text-lg">Gerencie seus treinos personalizados com IA</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
          <Button
            as={Link}
            to="/workouts/generate"
            icon={Plus}
            className="animate-slide-in-right"
          >
            Gerar Novo Treino
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card className="mb-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar treinos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          {/* Sort */}
          <div className="flex items-center space-x-2">
            <SortAsc className="h-5 w-5 text-gray-500" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="created_at">Mais recentes</option>
              <option value="name">Nome</option>
              <option value="intensity">Intensidade</option>
            </select>
          </div>
        </div>
        
        {/* Filter Tags */}
        <div className="flex items-center space-x-2 mt-4 pt-4 border-t border-gray-100">
          <Filter className="h-5 w-5 text-gray-500" />
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                filter === 'all'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Todos ({workouts.length})
            </button>
            {workoutTypes.map(type => (
              <button
                key={type}
                onClick={() => setFilter(type)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all capitalize ${
                  filter === type
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {type} ({workouts.filter(w => w.workout_type === type).length})
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Workouts Grid */}
      {filteredWorkouts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredWorkouts.map((workout, index) => (
            <Card key={workout.id} hover className={`card-hover animate-fade-in-up`} style={{animationDelay: `${index * 0.1}s`}}>
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getWorkoutTypeIcon(workout.workout_type)}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {workout.name || workout.workout_type}
                      </h3>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getIntensityColor(workout.intensity)}`}>
                        {workout.intensity}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => handleDeleteWorkout(workout.id)}
                      className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-3 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <Clock className="h-4 w-4 mr-2" />
                    <span>{formatDuration(workout.duration)}</span>
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <Target className="h-4 w-4 mr-2" />
                    <span className="capitalize">{workout.focus}</span>
                  </div>

                  {workout.rating && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Star className="h-4 w-4 mr-2 text-yellow-500" />
                      <span>{workout.rating}/5</span>
                    </div>
                  )}
                </div>

                {workout.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {workout.description}
                  </p>
                )}

                <div className="flex space-x-2">
                  <Link
                    to={`/workouts/${workout.id}`}
                    className="flex-1 inline-flex items-center justify-center px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Iniciar
                  </Link>
                  <Link
                    to={`/workouts/${workout.id}/edit`}
                    className="inline-flex items-center justify-center px-3 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-200 transition-colors"
                  >
                    <Edit className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Dumbbell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {filter === 'all' ? 'Nenhum treino encontrado' : `Nenhum treino de ${filter} encontrado`}
          </h3>
          <p className="text-gray-600 mb-6">
            Comece criando seu primeiro treino personalizado com nossa IA.
          </p>
          <Link
            to="/workouts/generate"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Gerar Primeiro Treino
          </Link>
        </div>
      )}
    </div>
  );
};

export default Workouts;