import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dietsAPI } from '../services/api';
import { ArrowLeft, Apple } from 'lucide-react';
import toast from 'react-hot-toast';

const GenerateDiet = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    goal: 'perda_peso',
    calories_target: 2000,
    meals_count: 5,
    dietary_restrictions: [],
    preferred_cuisine: 'brasileira'
  });

  const goals = [
    { value: 'perda_peso', label: 'Perda de Peso' },
    { value: 'ganho_massa', label: 'Ganho de Massa' },
    { value: 'manutencao', label: 'Manutenção' },
    { value: 'definicao', label: 'Definição' }
  ];

  const cuisines = [
    { value: 'brasileira', label: 'Brasileira' },
    { value: 'mediterranea', label: 'Mediterrânea' },
    { value: 'asiatica', label: 'Asiática' },
    { value: 'vegetariana', label: 'Vegetariana' },
    { value: 'vegana', label: 'Vegana' }
  ];

  const restrictions = [
    'Sem Glúten', 'Sem Lactose', 'Diabético', 'Hipertensão', 'Vegetariano', 'Vegano'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'calories_target' || name === 'meals_count' ? parseInt(value) : value
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
      const response = await dietsAPI.generateDiet(formData);
      toast.success('Dieta gerada com sucesso!');
      navigate('/diets');
    } catch (error) {
      console.error('Erro ao gerar dieta:', error);
      toast.error('Erro ao gerar dieta. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/diets')}
          className="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gerar Dieta</h1>
          <p className="text-gray-600">Crie um plano alimentar personalizado</p>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Objetivo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Objetivo
            </label>
            <select
              name="goal"
              value={formData.goal}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {goals.map(goal => (
                <option key={goal.value} value={goal.value}>
                  {goal.label}
                </option>
              ))}
            </select>
          </div>

          {/* Calorias Alvo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Calorias Diárias (kcal)
            </label>
            <input
              type="number"
              name="calories_target"
              value={formData.calories_target}
              onChange={handleChange}
              min="1200"
              max="4000"
              step="50"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          {/* Número de Refeições */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Número de Refeições por Dia
            </label>
            <select
              name="meals_count"
              value={formData.meals_count}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value={3}>3 refeições</option>
              <option value={4}>4 refeições</option>
              <option value={5}>5 refeições</option>
              <option value={6}>6 refeições</option>
            </select>
          </div>

          {/* Tipo de Culinária */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Culinária Preferida
            </label>
            <select
              name="preferred_cuisine"
              value={formData.preferred_cuisine}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {cuisines.map(cuisine => (
                <option key={cuisine.value} value={cuisine.value}>
                  {cuisine.label}
                </option>
              ))}
            </select>
          </div>

          {/* Restrições Alimentares */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Restrições Alimentares (opcional)
            </label>
            <div className="grid grid-cols-2 gap-2">
              {restrictions.map(restriction => (
                <label key={restriction} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.dietary_restrictions.includes(restriction)}
                    onChange={() => handleArrayChange('dietary_restrictions', restriction)}
                    className="mr-2"
                  />
                  <span className="text-sm">{restriction}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Gerando Dieta...
              </div>
            ) : (
              <>
                <Apple className="h-5 w-5 mr-2" />
                Gerar Dieta com IA
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default GenerateDiet;