import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dietsAPI } from '../services/api';
import { Apple, ArrowLeft, Zap } from 'lucide-react';
import toast from 'react-hot-toast';

const GenerateDiet = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    goal: 'perda_peso',
    calories: 2000,
    protein: 150,
    carbs: 200,
    fat: 70,
    meals: 5,
    dietary_restrictions: [],
    food_preferences: [],
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      if (name === 'dietary_restrictions' || name === 'food_preferences') {
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
        [name]: type === 'number' ? parseInt(value) : value
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await dietsAPI.registerDiet(formData);
      toast.success('Dieta criada com sucesso!');
      navigate('/diets');
    } catch (error) {
      console.error('Erro ao gerar dieta:', error);
      toast.error('Erro ao gerar dieta. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const restrictionOptions = [
    'Vegetariano', 'Vegano', 'Sem Glúten', 'Sem Lactose', 
    'Sem Açúcar', 'Low Carb', 'Cetogênica', 'Sem Nozes'
  ];

  const preferenceOptions = [
    'Frango', 'Peixe', 'Carne Vermelha', 'Ovos', 'Laticínios',
    'Frutas', 'Vegetais', 'Grãos', 'Leguminosas', 'Nozes'
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/diets')}
          className="p-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gerar Nova Dieta</h1>
          <p className="text-gray-600">Configure suas preferências para gerar uma dieta personalizada</p>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Objetivo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Objetivo da Dieta
            </label>
            <select
              name="goal"
              value={formData.goal}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="perda_peso">Perda de Peso</option>
              <option value="ganho_massa">Ganho de Massa</option>
              <option value="manutencao">Manutenção</option>
              <option value="definicao">Definição</option>
            </select>
          </div>

          {/* Calorias e Refeições */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Calorias Diárias
              </label>
              <input
                type="number"
                name="calories"
                value={formData.calories}
                onChange={handleChange}
                min="1200"
                max="4000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Número de Refeições
              </label>
              <select
                name="meals"
                value={formData.meals}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value={3}>3 refeições</option>
                <option value={4}>4 refeições</option>
                <option value={5}>5 refeições</option>
                <option value={6}>6 refeições</option>
              </select>
            </div>
          </div>

          {/* Macronutrientes */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-3">Macronutrientes (gramas)</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Proteínas
                </label>
                <input
                  type="number"
                  name="protein"
                  value={formData.protein}
                  onChange={handleChange}
                  min="50"
                  max="300"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Carboidratos
                </label>
                <input
                  type="number"
                  name="carbs"
                  value={formData.carbs}
                  onChange={handleChange}
                  min="50"
                  max="400"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gorduras
                </label>
                <input
                  type="number"
                  name="fat"
                  value={formData.fat}
                  onChange={handleChange}
                  min="30"
                  max="150"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>
          </div>

          {/* Restrições Alimentares */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Restrições Alimentares
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {restrictionOptions.map((restriction) => (
                <label key={restriction} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    name="dietary_restrictions"
                    value={restriction}
                    checked={formData.dietary_restrictions.includes(restriction)}
                    onChange={handleChange}
                    className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                  />
                  <span className="text-sm text-gray-700">{restriction}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Preferências Alimentares */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Preferências Alimentares
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {preferenceOptions.map((preference) => (
                <label key={preference} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    name="food_preferences"
                    value={preference}
                    checked={formData.food_preferences.includes(preference)}
                    onChange={handleChange}
                    className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                  />
                  <span className="text-sm text-gray-700">{preference}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => navigate('/diets')}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Gerando...
                </div>
              ) : (
                <div className="flex items-center">
                  <Zap className="h-4 w-4 mr-2" />
                  Gerar Dieta
                </div>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default GenerateDiet;