import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { workoutsAPI } from '../services/api';
import { Dumbbell, ArrowLeft, Zap } from 'lucide-react';
import toast from 'react-hot-toast';

const GenerateWorkout = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    workout_type: 'musculacao',
    intensity: 'moderada',
    duration_minutes: 45,
    focus: 'fullbody',
    equipment: [],
    muscle_groups: [],
    difficulty: 'intermediario',
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      if (name === 'equipment' || name === 'muscle_groups') {
        setFormData(prev => ({
          ...prev,
          [name]: checked 
            ? [...prev[name], value]
            : prev[name].filter(item => item !== value)
        }));
      }
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Converter duração para formato timedelta
      const duration = `${Math.floor(formData.duration_minutes / 60)}:${formData.duration_minutes % 60}:00`;
      
      const workoutData = {
        ...formData,
        duration: duration,
      };

      const response = await workoutsAPI.generateWorkout(workoutData);
      toast.success('Treino gerado com sucesso!');
      navigate('/workouts');
    } catch (error) {
      console.error('Erro ao gerar treino:', error);
      toast.error('Erro ao gerar treino. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const equipmentOptions = [
    'Halteres', 'Barras', 'Máquinas', 'Peso Corporal', 'Elásticos', 
    'Kettlebells', 'Medicine Ball', 'TRX', 'Banco'
  ];

  const muscleGroupOptions = [
    'Peito', 'Costas', 'Ombros', 'Bíceps', 'Tríceps', 
    'Quadríceps', 'Posterior', 'Glúteos', 'Panturrilha', 'Core'
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/workouts')}
          className="p-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gerar Novo Treino</h1>
          <p className="text-gray-600">Configure suas preferências para gerar um treino personalizado</p>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Tipo de Treino */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Treino
            </label>
            <select
              name="workout_type"
              value={formData.workout_type}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="musculacao">Musculação</option>
              <option value="cardio">Cardio</option>
              <option value="hiit">HIIT</option>
              <option value="yoga">Yoga</option>
              <option value="flexibilidade">Flexibilidade</option>
              <option value="strength">Força</option>
            </select>
          </div>

          {/* Intensidade e Duração */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Intensidade
              </label>
              <select
                name="intensity"
                value={formData.intensity}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="baixa">Baixa</option>
                <option value="moderada">Moderada</option>
                <option value="alta">Alta</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duração (minutos)
              </label>
              <input
                type="number"
                name="duration_minutes"
                value={formData.duration_minutes}
                onChange={handleChange}
                min="15"
                max="120"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Foco e Dificuldade */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Foco do Treino
              </label>
              <select
                name="focus"
                value={formData.focus}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="fullbody">Corpo Inteiro</option>
                <option value="upper_body">Membros Superiores</option>
                <option value="lower_body">Membros Inferiores</option>
                <option value="core">Core</option>
                <option value="cardio">Cardio</option>
                <option value="flexibility">Flexibilidade</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nível de Dificuldade
              </label>
              <select
                name="difficulty"
                value={formData.difficulty}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="iniciante">Iniciante</option>
                <option value="intermediario">Intermediário</option>
                <option value="avancado">Avançado</option>
              </select>
            </div>
          </div>

          {/* Equipamentos */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Equipamentos Disponíveis
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {equipmentOptions.map((equipment) => (
                <label key={equipment} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    name="equipment"
                    value={equipment}
                    checked={formData.equipment.includes(equipment)}
                    onChange={handleChange}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">{equipment}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Grupos Musculares */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Grupos Musculares (opcional)
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {muscleGroupOptions.map((muscle) => (
                <label key={muscle} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    name="muscle_groups"
                    value={muscle}
                    checked={formData.muscle_groups.includes(muscle)}
                    onChange={handleChange}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">{muscle}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => navigate('/workouts')}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Gerando...
                </div>
              ) : (
                <div className="flex items-center">
                  <Zap className="h-4 w-4 mr-2" />
                  Gerar Treino
                </div>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default GenerateWorkout;