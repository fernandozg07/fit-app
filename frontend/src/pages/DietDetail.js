import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { dietsAPI } from '../services/api';
import { 
  ArrowLeft, 
  Apple, 
  Target, 
  Calendar,
  Star,
  Clock,
  Utensils,
  Flame
} from 'lucide-react';
import toast from 'react-hot-toast';

const DietDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [diet, setDiet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [meals, setMeals] = useState([]);

  useEffect(() => {
    loadDiet();
  }, [id]);

  const loadDiet = async () => {
    try {
      const response = await dietsAPI.getDiet(id);
      setDiet(response.data);
      
      if (response.data.meals) {
        try {
          const parsedMeals = JSON.parse(response.data.meals);
          setMeals(Array.isArray(parsedMeals) ? parsedMeals : []);
        } catch (error) {
          console.error('Erro ao parsear refeições:', error);
          setMeals([]);
        }
      }
    } catch (error) {
      toast.error('Erro ao carregar dieta');
      navigate('/diets');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!diet) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Dieta não encontrada</h3>
        <button 
          onClick={() => navigate('/diets')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Voltar às dietas
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button 
          onClick={() => navigate('/diets')}
          className="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar
        </button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900">
            {diet.name || `Dieta ${diet.goal}`}
          </h1>
          <p className="text-gray-600">Detalhes do plano alimentar</p>
        </div>
      </div>

      {/* Diet Info */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-green-500 rounded-2xl shadow-lg">
              <Flame className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-green-700">Calorias Diárias</p>
              <p className="text-2xl font-bold text-green-900">{diet.calories} kcal</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-500 rounded-2xl shadow-lg">
              <Target className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-blue-700">Objetivo</p>
              <p className="text-lg font-semibold text-blue-900 capitalize">{diet.goal?.replace('_', ' ')}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-3 bg-purple-500 rounded-2xl shadow-lg">
              <Utensils className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-purple-700">Refeições</p>
              <p className="text-lg font-semibold text-purple-900">{meals.length || 5}/dia</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-3 bg-orange-500 rounded-2xl shadow-lg">
              <Calendar className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-orange-700">Criada em</p>
              <p className="text-lg font-semibold text-orange-900">
                {new Date(diet.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        {/* Macronutrients */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Proteínas</span>
              <span className="text-lg font-bold text-red-600">{diet.protein}g</span>
            </div>
          </div>

          <div className="bg-gray-50 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Carboidratos</span>
              <span className="text-lg font-bold text-blue-600">{diet.carbs}g</span>
            </div>
          </div>

          <div className="bg-gray-50 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Gorduras</span>
              <span className="text-lg font-bold text-yellow-600">{diet.fat}g</span>
            </div>
          </div>
        </div>

        {diet.description && (
          <div className="mt-6 p-4 bg-gray-50 rounded-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Descrição</h3>
            <p className="text-gray-700">{diet.description}</p>
          </div>
        )}
      </div>

      {/* Meals */}
      {meals.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Plano de Refeições</h2>
          <div className="space-y-4">
            {meals.map((meal, index) => (
              <div key={index} className="bg-gray-50 rounded-xl p-6 border">
                <div className="flex items-start space-x-4">
                  <div className="text-3xl">🍽️</div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      {meal.name || meal.type || `Refeição ${index + 1}`}
                    </h3>
                    {meal.time && (
                      <div className="flex items-center text-sm text-gray-600 mb-3">
                        <Clock className="h-4 w-4 mr-1" />
                        <span>{meal.time}</span>
                      </div>
                    )}
                    {meal.foods && (
                      <div className="space-y-2">
                        <h4 className="font-semibold text-gray-800">Alimentos:</h4>
                        <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {meal.foods.map((food, foodIndex) => (
                            <li key={foodIndex} className="flex items-center text-sm text-gray-700">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                              {food.name || food} {food.quantity && `- ${food.quantity}`}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {meal.calories && (
                      <div className="mt-3 inline-flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                        <Flame className="h-4 w-4 mr-1" />
                        {meal.calories} kcal
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DietDetail;