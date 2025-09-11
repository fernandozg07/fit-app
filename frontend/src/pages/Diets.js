import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dietsAPI } from '../services/api';
import { Apple, Plus, Flame, Target, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

const Diets = () => {
  const [diets, setDiets] = useState([]);
  const [loading, setLoading] = useState(true);

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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Minhas Dietas</h1>
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

      {/* Diets Grid */}
      {diets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {diets.map((diet) => (
            <div key={diet.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">🍎</span>
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
                    <Flame className="h-4 w-4 mr-2" />
                    <span>{diet.calories} kcal</span>
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <Target className="h-4 w-4 mr-2" />
                    <span className="capitalize">{diet.goal?.replace('_', ' ')}</span>
                  </div>
                </div>

                {diet.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {diet.description}
                  </p>
                )}

                <div className="grid grid-cols-3 gap-2 text-xs text-center">
                  <div className="bg-red-50 p-2 rounded">
                    <div className="font-semibold text-red-600">{diet.protein}g</div>
                    <div className="text-gray-600">Proteína</div>
                  </div>
                  <div className="bg-blue-50 p-2 rounded">
                    <div className="font-semibold text-blue-600">{diet.carbs}g</div>
                    <div className="text-gray-600">Carbos</div>
                  </div>
                  <div className="bg-yellow-50 p-2 rounded">
                    <div className="font-semibold text-yellow-600">{diet.fat}g</div>
                    <div className="text-gray-600">Gordura</div>
                  </div>
                </div>

                <div className="mt-4">
                  <Link
                    to={`/diets/${diet.id}`}
                    className="w-full inline-flex items-center justify-center px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition-colors"
                  >
                    Ver Detalhes
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
            Nenhuma dieta encontrada
          </h3>
          <p className="text-gray-600 mb-6">
            Comece criando seu primeiro plano alimentar personalizado.
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