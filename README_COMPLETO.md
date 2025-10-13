# 🏋️‍♂️ FIT-APP - Aplicação Completa de Fitness

Uma aplicação web completa para gerenciamento de treinos, dietas e progresso físico com inteligência artificial.

## 🚀 Funcionalidades

### 🔐 Autenticação
- Sistema completo de login/registro
- Autenticação JWT
- Perfil de usuário personalizado

### 💪 Treinos
- **Geração Inteligente**: Crie treinos personalizados com IA
- **Tipos Variados**: Musculação, Cardio, HIIT, Yoga
- **Níveis**: Iniciante, Intermediário, Avançado
- **Personalização**: Grupos musculares, equipamentos, duração
- **Acompanhamento**: Registre execução e feedback

### 🍎 Dietas
- **Planos Personalizados**: Dietas baseadas em objetivos
- **Objetivos**: Perda de peso, ganho de massa, manutenção, definição
- **Restrições**: Suporte a restrições alimentares
- **Macronutrientes**: Distribuição inteligente de proteínas, carboidratos e gorduras
- **Variedade**: Diferentes tipos de culinária

### 📊 Progresso
- **Acompanhamento Completo**: Peso, gordura corporal, massa muscular
- **Medidas Corporais**: Circunferências de braço, peito, cintura
- **Gráficos**: Visualização da evolução
- **Comparações**: Análise de progresso ao longo do tempo
- **Fotos**: Upload de fotos antes/depois

### 🤖 Chat IA
- Assistente virtual para dúvidas sobre fitness
- Dicas personalizadas
- Suporte 24/7

### 📈 Dashboard
- Visão geral do progresso
- Estatísticas de treinos e dietas
- Gráficos interativos
- Ações rápidas

## 🛠️ Tecnologias

### Backend
- **Django 4.2+**: Framework web robusto
- **Django REST Framework**: API RESTful
- **JWT**: Autenticação segura
- **SQLite/PostgreSQL**: Banco de dados
- **OpenAI API**: Inteligência artificial (opcional)
- **Swagger**: Documentação da API

### Frontend
- **React 18**: Interface moderna e responsiva
- **Tailwind CSS**: Estilização elegante
- **Recharts**: Gráficos interativos
- **React Router**: Navegação SPA
- **Axios**: Comunicação com API
- **React Hot Toast**: Notificações

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- npm ou yarn

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd fit-app
```

### 2. Configuração Automática
Execute o script de inicialização:
```bash
start-dev.bat
```

### 3. Configuração Manual

#### Backend
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

### 4. Variáveis de Ambiente

#### Backend (.env)
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
OPENAI_API_KEY=sua-chave-openai-opcional
```

#### Frontend (frontend/.env)
```env
REACT_APP_API_URL=http://localhost:8000
```

## 🌐 URLs Importantes

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **Documentação API**: http://localhost:8000/swagger
- **Redoc**: http://localhost:8000/redoc

## 📱 Como Usar

### 1. Registro e Login
1. Acesse http://localhost:3000
2. Clique em "Registrar" para criar uma conta
3. Preencha seus dados pessoais
4. Faça login com suas credenciais

### 2. Configurar Perfil
1. Vá para o perfil do usuário
2. Complete informações como peso, altura, objetivo
3. Defina restrições alimentares se necessário

### 3. Gerar Treino
1. Acesse "Treinos" → "Gerar Treino"
2. Selecione tipo, dificuldade e duração
3. Escolha grupos musculares e equipamentos
4. Clique em "Gerar Treino com IA"

### 4. Gerar Dieta
1. Acesse "Dietas" → "Gerar Dieta"
2. Defina objetivo e calorias diárias
3. Selecione número de refeições
4. Configure restrições alimentares
5. Clique em "Gerar Dieta com IA"

### 5. Acompanhar Progresso
1. Acesse "Progresso"
2. Clique em "Registrar Progresso"
3. Insira peso, medidas corporais
4. Adicione observações
5. Visualize gráficos de evolução

## 🔧 Estrutura do Projeto

```
fit-app/
├── backend/
│   ├── accounts/          # Autenticação e usuários
│   ├── workouts/          # Treinos
│   ├── diets/            # Dietas
│   ├── progress/         # Progresso
│   ├── chatbot/          # Chat IA
│   ├── ai/               # Inteligência artificial
│   └── fitness_app/      # Configurações Django
├── frontend/
│   ├── src/
│   │   ├── components/   # Componentes reutilizáveis
│   │   ├── pages/        # Páginas da aplicação
│   │   ├── contexts/     # Contextos React
│   │   ├── services/     # Serviços API
│   │   └── utils/        # Utilitários
│   └── public/           # Arquivos estáticos
└── docs/                 # Documentação
```

## 🎯 Funcionalidades Avançadas

### Geração Inteligente de Treinos
- Algoritmo que considera nível, objetivos e equipamentos
- Base de dados com centenas de exercícios
- Progressão automática baseada em feedback
- Variação para evitar monotonia

### Sistema de Dietas Personalizadas
- Cálculo automático de macronutrientes
- Distribuição inteligente entre refeições
- Receitas variadas e balanceadas
- Adaptação a restrições alimentares

### Análise de Progresso
- Gráficos de evolução temporal
- Comparações antes/depois
- Métricas de performance
- Exportação de dados

### Chat IA Integrado
- Respostas contextualizadas
- Dicas personalizadas
- Suporte a dúvidas comuns
- Histórico de conversas

## 🔒 Segurança

- Autenticação JWT segura
- Validação de dados no backend
- Proteção CORS configurada
- Sanitização de inputs
- Permissões por usuário

## 📊 API Endpoints

### Autenticação
- `POST /accounts/register/` - Registro
- `POST /accounts/token/` - Login
- `GET /accounts/users/me/` - Perfil

### Treinos
- `GET /workouts/` - Listar treinos
- `POST /workouts/generate/` - Gerar treino
- `GET /workouts/{id}/` - Detalhes do treino
- `POST /workouts/{id}/feedback/` - Feedback

### Dietas
- `GET /diets/` - Listar dietas
- `POST /diets/generate/` - Gerar dieta
- `GET /diets/{id}/` - Detalhes da dieta

### Progresso
- `GET /progress/` - Listar progresso
- `POST /progress/` - Adicionar registro
- `GET /progress/charts/` - Dados para gráficos

## 🚀 Deploy

### Desenvolvimento Local
```bash
# Backend
python manage.py runserver

# Frontend
cd frontend && npm start
```

### Produção
1. Configure variáveis de ambiente de produção
2. Execute `python manage.py collectstatic`
3. Configure servidor web (Nginx/Apache)
4. Use Gunicorn para servir Django
5. Build do React: `npm run build`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação
2. Consulte os logs de erro
3. Abra uma issue no GitHub
4. Entre em contato com a equipe

## 🎉 Próximas Funcionalidades

- [ ] App mobile React Native
- [ ] Integração com wearables
- [ ] Rede social fitness
- [ ] Marketplace de treinos
- [ ] Gamificação
- [ ] Análise avançada com ML
- [ ] Integração com nutricionistas
- [ ] Sistema de metas e conquistas

---

**Desenvolvido com ❤️ para a comunidade fitness**