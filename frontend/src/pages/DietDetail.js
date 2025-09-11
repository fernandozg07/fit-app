import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { dietsAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
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
  const [feedback, setFeedback] = useState({ rating: 5, comments: '' });
  const [showFeedback, setShowFeedback] = useState(false);

  useEffect(() => {
    loadDiet();
  }, [id]);

  const loadDiet = async () => {
    try {
      const response = await dietsAPI.getDiet(id);
      setDiet(response.data);
      
      // Parse meals if they exist
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

  const handleFeedback = async (e) => {
    e.preventDefault();
    try {
      // Assumindo que existe um endpoint de feedback para dietas
      await dietsAPI.sendFeedback(id, feedback);
      toast.success('Feedback enviado com sucesso!');
      setShowFeedback(false);
      loadDiet();
    } catch (error) {
      toast.error('Erro ao enviar feedback');
    }
  };

  const getMealIcon = (mealType) => {
    switch (mealType?.toLowerCase()) {
      case 'café da manhã':
      case 'breakfast':
        return '🌅';
      case 'almoço':
      case 'lunch':
        return '🍽️';
      case 'jantar':
      case 'dinner':
        return '🌙';
      case 'lanche':
      case 'snack':
        return '🍎';
      default:
        return '🍴';
    }
  };

  if (loading) {
    return <LoadingSpinner text="Carregando dieta..." />;
  }

  if (!diet) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Dieta não encontrada</h3>
        <Button onClick={() => navigate('/diets')}>
          Voltar às dietas
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button 
          variant="secondary" 
          size="sm"
          onClick={() => navigate('/diets')}
          icon={ArrowLeft}
        >
          Voltar
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900">
            {diet.name || `Dieta ${diet.goal}`}
          </h1>
          <p className="text-gray-600">Detalhes do plano alimentar</p>
        </div>
        <Button
          onClick={() => setShowFeedback(true)}
          icon={Star}
          variant="outline"
        >
          Avaliar Dieta
        </Button>
      </div>

      {/* Diet Info */}
      <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
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
              <p className="text-lg font-semibold text-purple-900">{meals.length || diet.meals || 5}/dia</p>
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
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Proteínas</span>
              <span className="text-lg font-bold text-red-600">{diet.protein}g</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div className="bg-red-500 h-2 rounded-full" style={{width: '30%'}}></div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Carboidratos</span>
              <span className="text-lg font-bold text-blue-600">{diet.carbs}g</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div className="bg-blue-500 h-2 rounded-full" style={{width: '50%'}}></div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Gorduras</span>
              <span className="text-lg font-bold text-yellow-600">{diet.fat}g</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div className="bg-yellow-500 h-2 rounded-full" style={{width: '20%'}}></div>
            </div>
          </div>
        </div>

        {diet.description && (
          <div className="mt-6 p-4 bg-white rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Descrição</h3>
            <p className="text-gray-700">{diet.description}</p>
          </div>
        )}
      </Card>

      {/* Meals */}
      {meals.length > 0 && (
        <Card>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Plano de Refeições</h2>
          <div className="space-y-4">
            {meals.map((meal, index) => (
              <div key={index} className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
                <div className="flex items-start space-x-4">
                  <div className="text-3xl">{getMealIcon(meal.type || meal.name)}</div>
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
        </Card>
      )}

      {/* Feedback Modal */}
      <Modal 
        isOpen={showFeedback} 
        onClose={() => setShowFeedback(false)}
        title="Avaliar Dieta"
      >
        <form onSubmit={handleFeedback} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Avaliação (1-5 estrelas)
            </label>
            <select
              value={feedback.rating}
              onChange={(e) => setFeedback({...feedback, rating: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Como está sendo seguir esta dieta? Alguma observação?"
            />
          </div>

          <div className="flex space-x-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setShowFeedback(false)}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="success"
              className="flex-1"
            >
              Enviar Avaliação
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default DietDetail;