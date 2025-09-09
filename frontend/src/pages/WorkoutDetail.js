import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { workoutsAPI } from '../services/api';
import { 
  ArrowLeft, 
  Clock, 
  Target, 
  Dumbbell,
  Star,
  Play,
  CheckCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const WorkoutDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [workout, setWorkout] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exercises, setExercises] = useState([]);
  const [feedback, setFeedback] = useState({ rating: 5, comments: '' });
  const [showFeedback, setShowFeedback] = useState(false);

  useEffect(() => {
    loadWorkout();
  }, [id]);

  const loadWorkout = async () => {
    try {
      const response = await workoutsAPI.getWorkout(id);
      setWorkout(response.data);
      
      // Parse exercises if they exist
      if (response.data.exercises) {
        try {
          const parsedExercises = JSON.parse(response.data.exercises);
          setExercises(Array.isArray(parsedExercises) ? parsedExercises : []);
        } catch (error) {
          console.error('Erro ao parsear exercícios:', error);
          setExercises([]);
        }
      }
    } catch (error) {
      toast.error('Erro ao carregar treino');
      navigate('/workouts');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (e) => {
    e.preventDefault();
    try {
      await workoutsAPI.sendFeedback(id, feedback);
      toast.success('Feedback enviado com sucesso!');
      setShowFeedback(false);
      loadWorkout();
    } catch (error) {
      toast.error('Erro ao enviar feedback');
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

  if (!workout) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Treino não encontrado</h3>
        <button
          onClick={() => navigate('/workouts')}
          className="text-blue-600 hover:underline"
        >
          Voltar aos treinos
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/workouts')}
          className="p-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">
            {workout.name || workout.workout_type}
          </h1>
          <p className="text-gray-600">Detalhes do treino</p>
        </div>
        <button
          onClick={() => setShowFeedback(true)}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Star className="h-4 w-4 mr-2" />
          Avaliar Treino
        </button>
      </div>

      {/* Workout Info */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 rounded-full">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Duração</p>
              <p className="font-semibold">{formatDuration(workout.duration)}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-3 bg-green-100 rounded-full">
              <Target className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Foco</p>
              <p className="font-semibold capitalize">{workout.focus}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-3 bg-purple-100 rounded-full">
              <Dumbbell className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Intensidade</p>
              <p className="font-semibold capitalize">{workout.intensity}</p>
            </div>
          </div>
        </div>

        {workout.description && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Descrição</h3>
            <p className="text-gray-700">{workout.description}</p>
          </div>
        )}

        {workout.muscle_groups && workout.muscle_groups.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Grupos Musculares</h3>
            <div className="flex flex-wrap gap-2">
              {workout.muscle_groups.map((group, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  {group}
                </span>
              ))}
            </div>
          </div>
        )}

        {workout.equipment && workout.equipment.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Equipamentos</h3>
            <div className="flex flex-wrap gap-2">
              {workout.equipment.map((item, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Exercises */}
      {exercises.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Exercícios</h2>
          <div className="space-y-4">
            {exercises.map((exercise, index) => (
              <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{exercise.name || exercise.exercise}</h3>
                  {exercise.description && (
                    <p className="text-gray-600 text-sm mt-1">{exercise.description}</p>
                  )}
                  <div className="flex space-x-4 mt-2 text-sm text-gray-600">
                    {exercise.sets && <span>Séries: {exercise.sets}</span>}
                    {exercise.reps && <span>Repetições: {exercise.reps}</span>}
                    {exercise.duration && <span>Duração: {exercise.duration}</span>}
                    {exercise.rest && <span>Descanso: {exercise.rest}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Feedback Modal */}
      {showFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Avaliar Treino</h2>
            <form onSubmit={handleFeedback} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Avaliação (1-5 estrelas)
                </label>
                <select
                  value={feedback.rating}
                  onChange={(e) => setFeedback({...feedback, rating: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={1}>1 - Muito Ruim</option>
                  <option value={2}>2 - Ruim</option>
                  <option value={3}>3 - Regular</option>
                  <option value={4}>4 - Bom</option>
                  <option value={5}>5 - Excelente</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Comentários (opcional)
                </label>
                <textarea
                  value={feedback.comments}
                  onChange={(e) => setFeedback({...feedback, comments: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Como foi o treino? Alguma observação?"
                />
              </div>

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setShowFeedback(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Enviar Avaliação
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkoutDetail;