# Fitness App Frontend

Frontend React para o aplicativo de fitness com IA integrada.

## 🚀 Funcionalidades

- ✅ **Autenticação completa** (Login/Registro)
- ✅ **Dashboard interativo** com estatísticas
- ✅ **Gerenciamento de treinos** (CRUD completo)
- ✅ **Gerenciamento de dietas** (CRUD completo)
- ✅ **Acompanhamento de progresso**
- ✅ **Chat com IA** para orientações
- ✅ **Design responsivo** (mobile-first)
- ✅ **Integração completa** com API Django

## 🛠️ Tecnologias

- **React 18** - Framework principal
- **React Router** - Navegação
- **Axios** - Requisições HTTP
- **React Hook Form** - Formulários
- **Lucide React** - Ícones
- **React Hot Toast** - Notificações
- **Recharts** - Gráficos
- **Tailwind CSS** - Estilização

## 📦 Instalação

1. **Instalar dependências:**
```bash
cd frontend
npm install
```

2. **Configurar variáveis de ambiente:**
Crie um arquivo `.env` na pasta frontend:
```
REACT_APP_API_URL=http://localhost:8000
```

3. **Iniciar o servidor de desenvolvimento:**
```bash
npm start
```

O app estará disponível em `http://localhost:3000`

## 🔧 Scripts Disponíveis

- `npm start` - Inicia o servidor de desenvolvimento
- `npm build` - Cria build de produção
- `npm test` - Executa os testes
- `npm run eject` - Ejeta a configuração do Create React App

## 📱 Páginas Implementadas

### Autenticação
- **Login** (`/login`) - Formulário de login com validação
- **Registro** (`/register`) - Cadastro completo com dados pessoais

### Área Logada
- **Dashboard** (`/dashboard`) - Visão geral com estatísticas
- **Treinos** (`/workouts`) - Lista e gerenciamento de treinos
- **Dietas** (`/diets`) - Lista e gerenciamento de dietas
- **Progresso** (`/progress`) - Acompanhamento de evolução
- **Chat IA** (`/chat`) - Conversa com assistente virtual

## 🔌 Integração com Backend

O frontend está totalmente integrado com a API Django:

### Endpoints Utilizados
- `POST /accounts/api/token/` - Login
- `POST /accounts/register/` - Registro
- `GET /accounts/api/users/me/` - Perfil do usuário
- `GET /workouts/` - Lista de treinos
- `POST /workouts/generate/` - Gerar treino com IA
- `GET /diets/api/diets/` - Lista de dietas
- `POST /diets/api/diets/generate/` - Gerar dieta com IA
- `GET /progress/` - Dados de progresso
- `POST /chat/` - Chat com IA

### Autenticação JWT
- Token de acesso armazenado no localStorage
- Renovação automática de tokens
- Interceptors para requisições autenticadas

## 🎨 Design System

### Cores Principais
- **Primária:** Azul (#667eea)
- **Secundária:** Roxo (#764ba2)
- **Sucesso:** Verde (#10b981)
- **Aviso:** Amarelo (#f59e0b)
- **Erro:** Vermelho (#ef4444)

### Componentes Reutilizáveis
- Layout com navegação responsiva
- Cards informativos
- Formulários padronizados
- Botões com estados
- Loading states
- Toast notifications

## 📊 Estado da Aplicação

### Context API
- **AuthContext** - Gerencia autenticação e dados do usuário
- Estados globais para login, logout, registro
- Carregamento automático do perfil

### Hooks Personalizados
- `useAuth()` - Hook para acessar contexto de autenticação
- Estados locais para cada página
- Gerenciamento de loading e erros

## 🔒 Segurança

- Rotas protegidas com ProtectedRoute
- Tokens JWT com renovação automática
- Validação de formulários
- Sanitização de dados
- Logout automático em caso de token inválido

## 📱 Responsividade

- Design mobile-first
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Menu hambúrguer para mobile
- Grid responsivo para cards
- Formulários adaptáveis

## 🚀 Deploy

Para fazer deploy em produção:

1. **Build da aplicação:**
```bash
npm run build
```

2. **Configurar variável de ambiente:**
```
REACT_APP_API_URL=https://sua-api-production.com
```

3. **Servir arquivos estáticos:**
Os arquivos da pasta `build/` podem ser servidos por qualquer servidor web.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.