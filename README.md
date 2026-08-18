# Fintech API - Dockerised Application

## Overview
A secure, containerised Fintech API built with FastAPI, PostgreSQL, and Redis.

## Features

### Core Functionality
- 🔐 JWT Authentication - Secure token-based authentication with refresh capability
- 💰 Transaction Processing - Suooort for deposits, Withdrawals, and transfers
- 🏦 Account Management - Real-time balance updates abd transaction history
- 🚀 Rate Limiting
- 📊 Health Checks - Built-in health checks and monitoring
- 📝 Comprehensive Logging - Structured logging with request/response tracking
- 🐳 Dockerised with multi-stage builds

### Security Features
- Password hashing with bcrypt
- JWT token expiration
- SQL injection prevention via SQLAlchemy
- Input validation with Pydantic
- Environment-based configuration

### DevOps Features
- Multi-stage builds
- Docker Compose orchestration
- Health checks for all services
- Database migrations
- CI/CD pipeline

### Tech Stack
- Python 3.11
- FastAPI
- PostgreSQL 15
- Redis 7
- Docker
- Docker Compose
- Github Actions

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

#### Create the project directory
```bash
mkdir fintechAPI && cd fintechAPI
```

#### Configure Environment
```bash
cp .env.example .env
```

#### Edit the env with your secure values
```bash
vi .env
```

#### Navigate to the docker directory
```bash
cd docker
```

#### Build and start the services
```bash
docker compose up -d --build api
```

#### Verify all services are running
```bash
docker compose ps
```

#### Watch logs
```bash
docker compose logs -f api
```

### Verify Installation

curl http://localhost:8000/health

#### Expected response
```json
{ "status": "healthy", "service": "fintech-api", "version", "1.0.0" }
```

### Testing
```bash
pytest
```

#### Access Points
- API http://localhost:8000
- API Docs http://localhost:8000/docs
- Adminer http://localhost:8001

| Method | Endpoint | Description |
| GET | /health | Health check |
| POST | /auth/register | Register user |
| POST | /auth/login | Authrnticate user |
| POST | /transactions/create | Create transactions |
| GET | /transactions | Get transactions |
