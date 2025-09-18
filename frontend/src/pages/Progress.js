import React, { useState, useEffect } from 'react';
import { progressAPI } from '../services/api';
import { Plus, Scale, TrendingUp, Trash2, BarChart3, Camera, Download } from 'lucide-react';
import toast from 'react-hot-toast';

const Progress = () => {
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showCharts, setShowCharts] = useState(false);
  const [chartData, setChartData] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [formData, setFormData] = useState({
    weight: '',
    body_fat: '',
    muscle_mass: '',
    arm_circumference: '',
    chest_circumference: '',
    waist_circumference: '',
    notes: ''
  });

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      const response = await progressAPI.getProgress();
      setProgress(Array.isArray(response.data) ? response.data : response.data.results || []);
      
      // Carrega dados de comparação se houver registros
      if (response.data.length > 1) {
        loadComparison();
      }
    } catch (error) {
      toast.error('Erro ao carregar progresso');
    } finally {
      setLoading(false);
    }
  };
  
  const loadComparison = async () => {
    try {
      const response = await progressAPI.getComparison();
      setComparison(response.data);
    } catch (error) {
      console.error('Erro ao carregar comparação:', error);
    }
  };
  
  const loadCharts = async () => {
    try {
      const response = await progressAPI.getCharts();
      setChartData(response.data);
      setShowCharts(true);
    } catch (error) {
      toast.error('Erro ao carregar gráficos');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await progressAPI.addProgress({
        ...formData,
        weight: parseFloat(formData.weight),
        body_fat: formData.body_fat ? parseFloat(formData.body_fat) : null,
        muscle_mass: formData.muscle_mass ? parseFloat(formData.muscle_mass) : null,
        arm_circumference: formData.arm_circumference ? parseFloat(formData.arm_circumference) : null,
        chest_circumference: formData.chest_circumference ? parseFloat(formData.chest_circumference) : null,
        waist_circumference: formData.waist_circumference ? parseFloat(formData.waist_circumference) : null,
        date: new Date().toISOString().split('T')[0]
      });
      toast.success('Progresso registrado com sucesso!');
      setShowForm(false);
      setFormData({ weight: '', body_fat: '', muscle_mass: '', arm_circumference: '', chest_circumference: '', waist_circumference: '', notes: '' });
      loadProgress();
    } catch (error) {
      toast.error('Erro ao registrar progresso');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir este registro?')) {
      try {
        await progressAPI.deleteProgress(id);
        setProgress(progress.filter(p => p.id !== id));
        toast.success('Registro excluído com sucesso!');
      } catch (error) {
        toast.error('Erro ao excluir registro');
      }
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Meu Progresso</h1>
          <p className="text-gray-600">Acompanhe sua evolução física</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowForm(!showForm)}
            className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Registrar Progresso
          </button>
          <button
            onClick={loadCharts}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <BarChart3 className="h-5 w-5 mr-2" />
            Ver Gráficos
          </button>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Novo Registro</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Peso (kg) *
                </label>
                <input
                  type="number"
                  name="weight"
                  value={formData.weight}
                  onChange={handleChange}
                  step="0.1"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Gordura Corporal (%)
                </label>
                <input
                  type="number"
                  name="body_fat"
                  value={formData.body_fat}
                  onChange={handleChange}
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Massa Muscular (kg)
                </label>
                <input
                  type="number"
                  name="muscle_mass"
                  value={formData.muscle_mass}
                  onChange={handleChange}
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Circunferência do Braço (cm)
                </label>
                <input
                  type="number"
                  name="arm_circumference"
                  value={formData.arm_circumference}
                  onChange={handleChange}
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Circunferência do Peito (cm)
                </label>
                <input
                  type="number"
                  name="chest_circumference"
                  value={formData.chest_circumference}
                  onChange={handleChange}
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Circunferência da Cintura (cm)
                </label>
                <input
                  type="number"
                  name="waist_circumference"
                  value={formData.waist_circumference}
                  onChange={handleChange}
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observações
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Como você está se sentindo? Alguma observação sobre sua evolução..."
              />
            </div>
            <div className="flex space-x-4">
              <button
                type="submit"
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                Salvar Registro
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Progress List */}
      {progress.length > 0 ? (
        <div className="space-y-4">
          {progress.map((entry) => (
            <div key={entry.id} className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-4 mb-3">
                    <div className="flex items-center space-x-2">
                      <Scale className="h-5 w-5 text-purple-600" />
                      <span className="text-lg font-semibold text-gray-900">
                        {entry.weight} kg
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(entry.date).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                    {entry.body_fat && (
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-4 w-4 text-orange-500" />
                        <span className="text-sm text-gray-600">
                          Gordura: {entry.body_fat}%
                        </span>
                      </div>
                    )}
                    {entry.muscle_mass && (
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-4 w-4 text-green-500" />
                        <span className="text-sm text-gray-600">
                          Músculo: {entry.muscle_mass} kg
                        </span>
                      </div>
                    )}
                  </div>
                  
                  {entry.notes && (
                    <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                      {entry.notes}
                    </p>
                  )}
                </div>
                
                <button
                  onClick={() => handleDelete(entry.id)}
                  className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Scale className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Nenhum registro encontrado
          </h3>
          <p className="text-gray-600 mb-6">
            Comece registrando seu progresso para acompanhar sua evolução.
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Primeiro Registro
          </button>
        </div>
      )}
    </div>
  );
};

export default Progress;