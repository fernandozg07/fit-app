import React, { useState, useEffect } from 'react';
import { progressAPI } from '../services/api';
import { 
  TrendingUp, 
  Plus, 
  Calendar,
  Scale,
  Ruler,
  Target,
  Activity
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import toast from 'react-hot-toast';

const Progress = () => {
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    weight: '',
    height: '',
    body_fat: '',
    muscle_mass: '',
    waist_circumference: '',
    chest_circumference: '',
    arm_circumference: '',
    leg_circumference: '',
    notes: '',
  });

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      const response = await progressAPI.getProgress();
      setProgress(Array.isArray(response.data) ? response.data : response.data.results || []);
    } catch (error) {
      toast.error('Erro ao carregar progresso');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {};
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '') {
          data[key] = key === 'notes' ? formData[key] : parseFloat(formData[key]);
        }
      });

      await progressAPI.addProgress(data);
      toast.success('Progresso registrado com sucesso!');
      setShowForm(false);
      setFormData({
        weight: '',
        height: '',
        body_fat: '',
        muscle_mass: '',
        waist_circumference: '',
        chest_circumference: '',
        arm_circumference: '',
        leg_circumference: '',
        notes: '',
      });
      loadProgress();
    } catch (error) {
      toast.error('Erro ao registrar progresso');
    }
  };

  const getLatestValue = (field) => {
    if (progress.length === 0) return null;
    const latest = progress[0];
    return latest[field] || null;
  };

  const getWeightData = () => {
    return progress
      .filter(p => p.weight)
      .map(p => ({
        date: new Date(p.date).toLocaleDateString(),
        weight: p.weight
      }))
      .reverse();
  };

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
          <h1 className="text-2xl font-bold text-gray-900">Meu Progresso</h1>
          <p className="text-gray-600">Acompanhe sua evolução física</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Registrar Medidas
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Registrar Novo Progresso</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Peso (kg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  name="weight"
                  value={formData.weight}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Altura (cm)
                </label>
                <input
                  type="number"
                  name="height"
                  value={formData.height}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Gordura Corporal (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  name="body_fat"
                  value={formData.body_fat}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Massa Muscular (kg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  name="muscle_mass"
                  value={formData.muscle_mass}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cintura (cm)
                </label>
                <input
                  type="number"
                  step="0.1"
                  name="waist_circumference"
                  value={formData.waist_circumference}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Peito (cm)
                </label>
                <input
                  type="number"
                  step="0.1"
                  name="chest_circumference"
                  value={formData.chest_circumference}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Braço (cm)
                </label>
                <input
                  type="number"
                  step="0.1"
                  name="arm_circumference"
                  value={formData.arm_circumference}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Perna (cm)
                </label>
                <input
                  type="number"
                  step="0.1"
                  name="leg_circumference"
                  value={formData.leg_circumference}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Como você se sente? Alguma observação sobre o treino ou dieta..."
              />
            </div>

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
              >
                Salvar Progresso
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Peso Atual</p>
              <p className="text-2xl font-bold text-gray-900">
                {getLatestValue('weight') ? `${getLatestValue('weight')} kg` : '--'}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Scale className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Gordura Corporal</p>
              <p className="text-2xl font-bold text-gray-900">
                {getLatestValue('body_fat') ? `${getLatestValue('body_fat')}%` : '--'}
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-full">
              <Target className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Massa Muscular</p>
              <p className="text-2xl font-bold text-gray-900">
                {getLatestValue('muscle_mass') ? `${getLatestValue('muscle_mass')} kg` : '--'}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Registros</p>
              <p className="text-2xl font-bold text-gray-900">{progress.length}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Weight Chart */}
      {getWeightData().length > 0 && (
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Evolução do Peso</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={getWeightData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="weight" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  dot={{ fill: '#8884d8' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Progress History */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Histórico de Progresso</h2>
        </div>
        <div className="p-6">
          {progress.length > 0 ? (
            <div className="space-y-4">
              {progress.map((entry) => (
                <div key={entry.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-purple-100 rounded-full">
                      <Calendar className="h-5 w-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {new Date(entry.date).toLocaleDateString()}
                      </p>
                      <div className="flex space-x-4 text-sm text-gray-600">
                        {entry.weight && <span>Peso: {entry.weight}kg</span>}
                        {entry.body_fat && <span>Gordura: {entry.body_fat}%</span>}
                        {entry.muscle_mass && <span>Músculo: {entry.muscle_mass}kg</span>}
                      </div>
                    </div>
                  </div>
                  {entry.notes && (
                    <div className="text-sm text-gray-600 max-w-xs">
                      {entry.notes}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Nenhum progresso registrado
              </h3>
              <p className="text-gray-600 mb-4">
                Comece registrando suas medidas para acompanhar sua evolução.
              </p>
              <button
                onClick={() => setShowForm(true)}
                className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <Plus className="h-5 w-5 mr-2" />
                Registrar Primeiro Progresso
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Progress;