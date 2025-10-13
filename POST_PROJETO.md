# 🏋️‍♂️ FIT-APP - Aplicação Completa de Fitness com IA

## 🚀 Sobre o Projeto

Desenvolvi uma aplicação web completa para gerenciamento de treinos, dietas e progresso físico, utilizando **inteligência artificial** para personalização. O projeto combina **Django REST API** no backend e **React** no frontend, oferecendo uma experiência moderna e intuitiva.

## ✨ Principais Funcionalidades

### 🤖 **Geração Inteligente com IA**
- **Treinos Personalizados**: Algoritmo que considera nível, objetivos e equipamentos disponíveis
- **Dietas Balanceadas**: Cálculo automático de macronutrientes e distribuição entre refeições
- **Base de Dados Local**: 100+ exercícios categorizados por tipo, dificuldade e foco muscular
- **Fallback Robusto**: Sistema funciona mesmo sem API externa de IA

### 📊 **Dashboard Interativo**
- **Gráficos em Tempo Real**: Visualização de progresso com Recharts
- **Estatísticas Detalhadas**: Métricas de treinos, dietas e evolução física
- **Ações Rápidas**: Acesso direto às funcionalidades principais
- **Interface Responsiva**: Design moderno com Tailwind CSS

### 💪 **Sistema de Treinos**
- **Tipos Variados**: Musculação, Cardio, HIIT, Yoga, Flexibilidade
- **Níveis Adaptativos**: Iniciante, Intermediário, Avançado
- **Personalização Total**: Grupos musculares, equipamentos, duração (15-120min)
- **Feedback Inteligente**: Sistema aprende com suas avaliações

### 🍎 **Planos Alimentares**
- **Objetivos Específicos**: Perda de peso, ganho de massa, manutenção, definição
- **Restrições Alimentares**: Vegetariano, vegano, sem glúten, sem lactose
- **Cálculo Preciso**: Distribuição inteligente de proteínas, carboidratos e gorduras
- **Receitas Variadas**: Sugestões adaptadas ao tipo de culinária preferida

### 📈 **Acompanhamento de Progresso**
- **Métricas Completas**: Peso, gordura corporal, massa muscular
- **Medidas Corporais**: Circunferências de braço, peito, cintura, quadril
- **Evolução Visual**: Gráficos de linha e barras para análise temporal
- **Comparações**: Análise de progresso com dados históricos

## 🛠️ Tecnologias Utilizadas

### **Backend (Django)**
```python
# Stack Principal
- Django 4.2+ (Framework web robusto)
- Django REST Framework (API RESTful)
- JWT Authentication (Segurança)
- SQLite/PostgreSQL (Banco de dados)
- OpenAI API (IA opcional)
- Swagger/Redoc (Documentação automática)
```

### **Frontend (React)**
```javascript
// Stack Moderno
- React 18 (Interface dinâmica)
- Tailwind CSS (Estilização elegante)
- Recharts (Gráficos interativos)
- React Router (SPA Navigation)
- Axios (HTTP Client)
- React Hot Toast (Notificações)
```

## 🎯 Destaques Técnicos

### **Arquitetura Robusta**
- **API REST Completa**: Endpoints documentados com Swagger
- **Autenticação JWT**: Sistema seguro de login/registro
- **Filtros Avançados**: Busca e paginação em todas as listagens
- **Validação de Dados**: Serializers Django com validação customizada

### **Algoritmos Inteligentes**
```python
def generate_local_exercises(workout_type, muscle_groups, equipment, difficulty, duration_minutes, num_exercises):
    """Gera exercícios localmente baseado nos parâmetros"""
    # Lógica inteligente de seleção de exercícios
    # Considera tipo, dificuldade, equipamentos e duração
    # Retorna exercícios personalizados
```

### **Interface Moderna**
```jsx
// Dashboard com gráficos interativos
<ResponsiveContainer width="100%" height={200}>
  <LineChart data={progressData}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="date" />
    <YAxis />
    <Tooltip />
    <Line type="monotone" dataKey="weight" stroke="#3b82f6" strokeWidth={2} />
  </LineChart>
</ResponsiveContainer>
```

## 📱 Screenshots e Demonstração

### **Dashboard Principal**
- Visão geral com estatísticas
- Gráficos de progresso em tempo real
- Ações rápidas para gerar treinos/dietas
- Cards informativos com métricas

### **Geração de Treinos**
- Formulário intuitivo de personalização
- Seleção de grupos musculares
- Configuração de equipamentos
- Preview do treino gerado

### **Acompanhamento de Progresso**
- Formulário de registro de medidas
- Gráficos de evolução temporal
- Comparações antes/depois
- Exportação de dados

## 🚀 Como Executar

### **Configuração Rápida**
```bash
# 1. Clone o repositório
git clone [url-do-repo]
cd fit-app

# 2. Execute o script de setup
start-dev.bat

# 3. Inicie os servidores
# Backend: python manage.py runserver
# Frontend: cd frontend && npm start
```

### **Acesso**
- **Aplicação**: http://localhost:3000
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/swagger
- **Admin**: http://localhost:8000/admin

## 🎯 Funcionalidades em Destaque

### **1. Geração Inteligente de Treinos**
```python
# Exemplo de treino gerado
{
  "name": "Treino Upper Body - Intermediário (45min)",
  "exercises": [
    {
      "name": "Flexão de Braço",
      "sets": "3",
      "reps": "12-20",
      "instructions": "Mantenha o corpo reto..."
    }
  ],
  "duration": "45 minutos",
  "difficulty": "intermediario"
}
```

### **2. Planos Alimentares Personalizados**
```python
# Exemplo de dieta gerada
{
  "target_calories": 2000,
  "meals": [
    {
      "meal": "breakfast",
      "name": "Omelete com Espinafre",
      "calories": 400,
      "protein": 25,
      "carbs": 15,
      "fat": 12
    }
  ]
}
```

### **3. Dashboard com Métricas**
- **Total de Treinos**: Contador dinâmico
- **Dietas Criadas**: Histórico completo
- **Progresso Semanal**: Gráfico de barras
- **Peso Atual**: Última medição registrada

## 🔧 Arquitetura do Sistema

### **Backend (Django)**
```
fit-app/
├── accounts/          # Autenticação e usuários
├── workouts/          # Sistema de treinos
├── diets/            # Planos alimentares
├── progress/         # Acompanhamento
├── chatbot/          # IA conversacional
├── ai/               # Algoritmos de IA
└── fitness_app/      # Configurações
```

### **Frontend (React)**
```
frontend/src/
├── components/       # Componentes reutilizáveis
├── pages/           # Páginas da aplicação
├── contexts/        # Gerenciamento de estado
├── services/        # Comunicação com API
└── utils/           # Utilitários
```

## 📊 Métricas do Projeto

- **Linhas de Código**: 5000+ (Backend + Frontend)
- **Endpoints API**: 25+ endpoints documentados
- **Componentes React**: 15+ componentes reutilizáveis
- **Exercícios na Base**: 100+ exercícios categorizados
- **Tipos de Treino**: 5 modalidades diferentes
- **Objetivos de Dieta**: 4 objetivos específicos

## 🎯 Diferenciais

### **1. IA Híbrida**
- Integração com OpenAI (opcional)
- Sistema local robusto como fallback
- Aprendizado baseado em feedback

### **2. UX/UI Moderna**
- Design responsivo e intuitivo
- Gráficos interativos
- Notificações em tempo real
- Navegação fluida (SPA)

### **3. Escalabilidade**
- Arquitetura modular
- API REST bem estruturada
- Banco de dados otimizado
- Deploy-ready

## 🚀 Próximas Funcionalidades

- [ ] **App Mobile**: React Native
- [ ] **Integração Wearables**: Smartwatches
- [ ] **Rede Social**: Compartilhamento de treinos
- [ ] **Gamificação**: Sistema de conquistas
- [ ] **ML Avançado**: Predição de resultados
- [ ] **Marketplace**: Treinos premium

## 🤝 Contribuições

O projeto está aberto para contribuições! Principais áreas:

- **Novos Exercícios**: Expandir base de dados
- **Algoritmos IA**: Melhorar personalização
- **Interface**: Novos componentes
- **Testes**: Cobertura de testes
- **Documentação**: Guias e tutoriais

## 📝 Conclusão

O **FIT-APP** representa uma solução completa para o mercado fitness, combinando tecnologias modernas com algoritmos inteligentes. O projeto demonstra:

✅ **Arquitetura Full-Stack** robusta e escalável
✅ **Integração de IA** para personalização
✅ **Interface Moderna** e responsiva
✅ **Funcionalidades Completas** para fitness
✅ **Código Limpo** e bem documentado

---

## 🔗 Links Úteis

- **Repositório**: [GitHub Link]
- **Demo Online**: [Deploy Link]
- **Documentação**: [Docs Link]
- **LinkedIn**: [Seu LinkedIn]

## 🏷️ Tags

`#Django` `#React` `#IA` `#Fitness` `#FullStack` `#Python` `#JavaScript` `#API` `#WebDev` `#TailwindCSS` `#JWT` `#Swagger` `#OpenAI` `#HealthTech`

---

**💡 Desenvolvido com paixão por tecnologia e fitness!**

*Se você gostou do projeto, deixe uma ⭐ no repositório e compartilhe com a comunidade!*