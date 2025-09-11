import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { workoutsAPI } from '../services/api';
import { ArrowLeft, Dumbbell } from 'lucide-react';
import toast from 'react-hot-toast';

const GenerateWorkout = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    workout_type: 'musculacao',
    difficulty: 'iniciante',
    duration: 30,
    muscle_groups: [],
    equipment: [],
    intensity: 'moderada'
  });

  const workoutTypes = [
    { value: 'musculacao', label: 'Musculação' },
    { value: 'cardio', label: 'Cardio' },
    { value: 'hiit', label: 'HIIT' },
    { value: 'yoga', label: 'Yoga' }
  ];

  const difficulties = [
    { value: 'iniciante', label: 'Iniciante' },
    { value: 'intermediario', label: 'Intermediário' },
    { value: 'avancado', label: 'Avançado' }
  ];

  const intensities = [
    { value: 'baixa', label: 'Baixa' },
    { value: 'moderada', label: 'Moderada' },
    { value: 'alta', label: 'Alta' }
  ];

  const muscleGroups = [
    'Peito', 'Costas', 'Ombros', 'Braços', 'Pernas', 'Abdomen', 'Glúteos'
  ];

  const equipments = [
    'Halteres', 'Barras', 'Máquinas', 'Peso Corporal', 'Elásticos', 'Kettlebell'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleArrayChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: prev[name].includes(value)
        ? prev[name].filter(item => item !== value)
        : [...prev[name], value]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await workoutsAPI.generateWorkout(formData);
      toast.success('Treino gerado com sucesso!');
      navigate('/workouts');
    } catch (error) {
      console.error('Erro ao gerar treino:', error);
      toast.error('Erro ao gerar treino. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/workouts')}
          className="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gerar Treino</h1>
          <p className="text-gray-600">Crie um treino personalizado com IA</p>
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {workoutTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Dificuldade */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Dificuldade
            </label>
            <select
              name="difficulty"
              value={formData.difficulty}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {difficulties.map(diff => (
                <option key={diff.value} value={diff.value}>
                  {diff.label}
                </option>
              ))}
            </select>
          </div>

          {/* Duração */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duração (minutos)
            </label>
            <input
              type="number"
              name="duration"
              value={formData.duration}
              onChange={handleChange}
              min="15"
              max="120"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Intensidade */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Intensidade
            </label>
            <select
              name="intensity"
              value={formData.intensity}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {intensities.map(intensity => (
                <option key={intensity.value} value={intensity.value}>
                  {intensity.label}
                </option>
              ))}
            </select>
          </div>

          {/* Grupos Musculares */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Grupos Musculares (opcional)
            </label>
            <div className="grid grid-cols-2 gap-2">
              {muscleGroups.map(group => (
                <label key={group} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.muscle_groups.includes(group)}
                    onChange={() => handleArrayChange('muscle_groups', group)}
                    className="mr-2"
                  />
                  <span className="text-sm">{group}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Equipamentos */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Equipamentos Disponíveis (opcional)
            </label>
            <div className="grid grid-cols-2 gap-2">
              {equipments.map(equipment => (
                <label key={equipment} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.equipment.includes(equipment)}
                    onChange={() => handleArrayChange('equipment', equipment)}
                    className="mr-2"
                  />
                  <span className="text-sm">{equipment}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Gerando Treino...
              </div>
            ) : (
              <>
                <Dumbbell className="h-5 w-5 mr-2" />
                Gerar Treino com IA
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default GenerateWorkout;