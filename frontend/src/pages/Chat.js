import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';
import { MessageCircle, Send, Bot, User } from 'lucide-react';
import toast from 'react-hot-toast';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const response = await chatAPI.getChatHistory();
      setMessages(Array.isArray(response.data) ? response.data : response.data.results || []);
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    } finally {
      setInitialLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      message: newMessage,
      user_message: newMessage,
      bot_response: '',
      created_at: new Date().toISOString(),
      isTemporary: true
    };

    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(newMessage);
      
      // Remove a mensagem temporária e adiciona a resposta real
      setMessages(prev => {
        const filtered = prev.filter(msg => !msg.isTemporary);
        return [...filtered, response.data];
      });
    } catch (error) {
      toast.error('Erro ao enviar mensagem');
      // Remove a mensagem temporária em caso de erro
      setMessages(prev => prev.filter(msg => !msg.isTemporary));
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (initialLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-200px)] flex flex-col">
      {/* Header */}
      <div className="bg-white rounded-t-lg shadow-sm border-b p-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-full">
            <Bot className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Assistente de Fitness IA</h1>
            <p className="text-sm text-gray-600">Tire suas dúvidas sobre treinos, dietas e exercícios</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 bg-white overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Bem-vindo ao Chat IA!
            </h3>
            <p className="text-gray-600 mb-6">
              Faça perguntas sobre treinos, dietas, exercícios ou qualquer dúvida relacionada ao fitness.
            </p>
            <div className="bg-gray-50 rounded-lg p-4 max-w-md mx-auto">
              <p className="text-sm text-gray-700 font-medium mb-2">Exemplos de perguntas:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• "Como fazer flexão corretamente?"</li>
                <li>• "Qual a melhor dieta para ganhar massa?"</li>
                <li>• "Quantas vezes treinar por semana?"</li>
                <li>• "Como calcular meu gasto calórico?"</li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={message.id || `message-${index}`} className="space-y-4">
              {/* User Message */}
              {message.user_message && (
                <div className="flex justify-end">
                  <div className="flex items-start space-x-2 max-w-xs lg:max-w-md">
                    <div className="bg-blue-600 text-white rounded-lg px-4 py-2">
                      <p className="text-sm">{message.user_message}</p>
                      <p className="text-xs text-blue-100 mt-1">
                        {formatTime(message.created_at)}
                      </p>
                    </div>
                    <div className="p-1 bg-blue-100 rounded-full">
                      <User className="h-4 w-4 text-blue-600" />
                    </div>
                  </div>
                </div>
              )}

              {/* Bot Response */}
              {message.bot_response && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2 max-w-xs lg:max-w-md">
                    <div className="p-1 bg-gray-100 rounded-full">
                      <Bot className="h-4 w-4 text-gray-600" />
                    </div>
                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                      <p className="text-sm text-gray-800 whitespace-pre-wrap">
                        {message.bot_response}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatTime(message.created_at)}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Loading indicator for temporary message */}
              {message.isTemporary && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2 max-w-xs lg:max-w-md">
                    <div className="p-1 bg-gray-100 rounded-full">
                      <Bot className="h-4 w-4 text-gray-600" />
                    </div>
                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                        <span className="text-sm text-gray-600">Pensando...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white rounded-b-lg shadow-sm border-t p-4">
        <form onSubmit={handleSendMessage} className="flex space-x-4">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Digite sua pergunta sobre fitness..."
            disabled={loading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !newMessage.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Send className="h-4 w-4" />
            )}
            <span>Enviar</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;