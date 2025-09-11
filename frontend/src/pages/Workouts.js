import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { workoutsAPI } from '../services/api';
import { 
  Dumbbell, 
  Plus, 
  Clock, 
  Target, 
  Star,
  Trash2,
  Edit,
  Play
} from 'lucide-react';
import toast from 'react-hot-toast';

const Workouts = () => {
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadWorkouts();
  }, []);

  const loadWorkouts = async () => {
    try {
      const response = await workoutsAPI.getWorkouts();
      setWorkouts(Array.isArray(response.data) ? response.data : response.data.results || []);
    } catch (error) {
      toast.error('Erro ao carregar treinos');
    } finally {
      setLoading(false);
    }
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
      case 'cardio': return '🏃♂️';
      case 'musculacao': return '💪';
      case 'yoga': return '🧘♀️';
      case 'hiit': return '⚡';
      default: return '🎯';
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

  const filteredWorkouts = workouts.filter(workout => {
    if (filter === 'all') return true;
    return workout.workout_type === filter;
  });

  const workoutTypes = [...new Set(workouts.map(w => w.workout_type))];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Meus Treinos</h1>
          <p className="text-gray-600">Gerencie seus treinos personalizados</p>
        </div>
        <Link
          to="/workouts/generate"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Gerar Novo Treino
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg p-4 shadow-sm border">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Todos ({workouts.length})
          </button>
          {workoutTypes.map(type => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors capitalize ${
                filter === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {type} ({workouts.filter(w => w.workout_type === type).length})
            </button>
          ))}
        </div>
      </div>

      {/* Workouts Grid */}
      {filteredWorkouts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredWorkouts.map((workout) => (
            <div key={workout.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getWorkoutTypeIcon(workout.workout_type)}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {workout.name || workout.workout_type}
                      </h3>
                      <span className="inline-block px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                        {workout.intensity}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteWorkout(workout.id)}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
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

                <div className="flex space-x-2">
                  <Link
                    to={`/workouts/${workout.id}`}
                    className="flex-1 inline-flex items-center justify-center px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Ver Detalhes
                  </Link>
                  <button className="inline-flex items-center justify-center px-3 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-200 transition-colors">
                    <Edit className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Dumbbell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Nenhum treino encontrado
          </h3>
          <p className="text-gray-600 mb-6">
            Comece criando seu primeiro treino personalizado.
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