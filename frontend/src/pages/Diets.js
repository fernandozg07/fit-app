import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dietsAPI } from '../services/api';
import { 
  Apple, 
  Plus, 
  Calendar, 
  Target, 
  Star,
  Trash2,
  Edit,
  Play,
  Filter
} from 'lucide-react';
import toast from 'react-hot-toast';

const Diets = () => {
  const [diets, setDiets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadDiets();
  }, []);

  const loadDiets = async () => {
    try {
      const response = await dietsAPI.getDiets();
      setDiets(Array.isArray(response.data) ? response.data : response.data.results || []);
    } catch (error) {
      toast.error('Erro ao carregar dietas');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDiet = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir esta dieta?')) {
      try {
        await dietsAPI.deleteDiet(id);
        setDiets(diets.filter(d => d.id !== id));
        toast.success('Dieta excluída com sucesso!');
      } catch (error) {
        toast.error('Erro ao excluir dieta');
      }
    }
  };

  const getGoalIcon = (goal) => {
    switch (goal) {
      case 'perda_peso':
        return '📉';
      case 'ganho_massa':
        return '📈';
      case 'manutencao':
        return '⚖️';
      default:
        return '🎯';
    }
  };

  const filteredDiets = diets.filter(diet => {
    if (filter === 'all') return true;
    return diet.goal === filter;
  });

  const dietGoals = [...new Set(diets.map(d => d.goal))];

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
          <h1 className="text-2xl font-bold text-gray-900">Minhas Dietas</h1>
          <p className="text-gray-600">Gerencie seus planos alimentares</p>
        </div>
        <Link
          to="/diets/generate"
          className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Gerar Nova Dieta
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg p-4 shadow-sm border">
        <div className="flex items-center space-x-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Todas ({diets.length})
            </button>
            {dietGoals.map(goal => (
              <button
                key={goal}
                onClick={() => setFilter(goal)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors capitalize ${
                  filter === goal
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {goal.replace('_', ' ')} ({diets.filter(d => d.goal === goal).length})
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Diets Grid */}
      {filteredDiets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDiets.map((diet) => (
            <div key={diet.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getGoalIcon(diet.goal)}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {diet.name || `Dieta ${diet.goal}`}
                      </h3>
                      <span className="inline-block px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 capitalize">
                        {diet.goal?.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteDiet(diet.id)}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>

                <div className="space-y-3 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <Target className="h-4 w-4 mr-2" />
                    <span>{diet.calories} kcal/dia</span>
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    <span>Criada em {new Date(diet.created_at).toLocaleDateString()}</span>
                  </div>

                  {diet.rating && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Star className="h-4 w-4 mr-2 text-yellow-500" />
                      <span>{diet.rating}/5</span>
                    </div>
                  )}
                </div>

                {diet.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {diet.description}
                  </p>
                )}

                <div className="flex space-x-2">
                  <Link
                    to={`/diets/${diet.id}`}
                    className="flex-1 inline-flex items-center justify-center px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition-colors"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Ver Detalhes
                  </Link>
                  <Link
                    to={`/diets/${diet.id}/edit`}
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
          <Apple className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {filter === 'all' ? 'Nenhuma dieta encontrada' : `Nenhuma dieta de ${filter.replace('_', ' ')} encontrada`}
          </h3>
          <p className="text-gray-600 mb-6">
            Comece criando sua primeira dieta personalizada com nossa IA.
          </p>
          <Link
            to="/diets/generate"
            className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Gerar Primeira Dieta
          </Link>
        </div>
      )}
    </div>
  );
};

export default Diets;