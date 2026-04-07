# AI Mind Map CRM

An AI-powered Customer Relationship Management system with interactive mind map visualization, helping teams understand and navigate customer relationships intuitively.

## Features

- 🧠 **Mind Map Visualization** – Explore customer relationships, deals, and contacts as an interactive graph
- 🤖 **AI Insights** – GPT-powered summaries, next-action suggestions, and relationship scoring
- 📋 **CRM Core** – Contacts, companies, deals, activities, and pipeline management
- 🔐 **Authentication** – JWT-based auth with role-based access control
- 📊 **Dashboard** – Real-time metrics and activity feed

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, ReactFlow, Zustand, TailwindCSS |
| Backend | Node.js, Express, TypeScript |
| Database | PostgreSQL + Prisma ORM |
| AI | OpenAI GPT-4 API |
| DevOps | Docker Compose, GitHub Actions |

## Getting Started

### Prerequisites

- Node.js ≥ 18
- Docker & Docker Compose
- OpenAI API key

### 1. Clone & install

```bash
git clone https://github.com/senarzuniga/AI-Mind-Map-CRM.git
cd AI-Mind-Map-CRM
cp .env.example .env          # fill in secrets
```

### 2. Start the database

```bash
docker compose up -d db
```

### 3. Backend

```bash
cd backend
npm install
npx prisma migrate dev
npm run dev
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at **http://localhost:5173**  
The API runs on **http://localhost:3001**

### Full stack with Docker

```bash
docker compose up --build
```

## Project Structure

```
AI-Mind-Map-CRM/
├── backend/          # Express API + Prisma
│   ├── prisma/       # Database schema & migrations
│   └── src/
│       ├── controllers/
│       ├── middleware/
│       ├── routes/
│       ├── services/
│       └── utils/
├── frontend/         # React SPA
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       ├── services/
│       ├── store/
│       └── types/
└── .github/workflows/ # CI pipeline
```

## Environment Variables

See [`.env.example`](./.env.example) for all required variables.

## License

MIT
