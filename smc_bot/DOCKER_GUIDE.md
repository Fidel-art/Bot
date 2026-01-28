# Docker Deployment Guide

## 🐳 Docker Compose Setup

### Prerequisites
- Docker Desktop installed
- Docker Compose v3.8+

### Quick Start

1. **Clone/Navigate to project:**
```powershell
cd "C:\Users\FidelSomba\OneDrive\Desktop\BOT code\smc_bot"
```

2. **Create environment file:**
```powershell
copy .env.example .env
# Edit .env with your configuration
```

3. **Build and start all services:**
```powershell
docker-compose up --build
```

4. **Access services:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Service Management

**Start services:**
```powershell
docker-compose up -d
```

**Stop services:**
```powershell
docker-compose down
```

**View logs:**
```powershell
docker-compose logs -f
```

**Restart a service:**
```powershell
docker-compose restart backend
```

**Rebuild after changes:**
```powershell
docker-compose up --build
```

## 📦 Services

### Backend (Port 8000)
- FastAPI REST API
- Authentication & JWT
- Bot management
- Database operations

### Frontend (Port 3000)
- React web application
- Vite dev server
- Hot module reload

### Database
- SQLite database container
- Persistent volume at `./data`

### Bot Core (Optional)
Uncomment in docker-compose.yml to run trading bot in container.

## 🔧 Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-secret-key-here
DATABASE_PATH=/app/data/bot_dashboard.db
VITE_API_URL=http://localhost:8000
MT5_LOGIN=your_login
MT5_PASSWORD=your_password
MT5_SERVER=your_server
```

### Volumes
- `./data` - Database and persistent data
- `./logs` - Application logs
- `./backend` - Backend code (hot reload)
- `./frontend` - Frontend code (hot reload)

## 🚀 Production Deployment

### Build for production:
```powershell
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### Production optimizations:
1. Set `NODE_ENV=production`
2. Build frontend: `npm run build`
3. Use production secret key
4. Disable reload in uvicorn
5. Add nginx reverse proxy
6. Use SSL certificates

## 🔍 Troubleshooting

**Port already in use:**
```powershell
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Backend
  - "3001:3000"  # Frontend
```

**Database permission errors:**
```powershell
# Ensure data directory exists
mkdir data
```

**Frontend not connecting to backend:**
- Check VITE_API_URL in .env
- Verify backend is running: http://localhost:8000/docs

**Container won't start:**
```powershell
# View logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild
docker-compose down
docker-compose up --build
```

## 📊 Docker Commands Reference

```powershell
# List running containers
docker-compose ps

# Execute command in container
docker-compose exec backend python -c "print('test')"

# View container logs
docker-compose logs -f backend

# Remove all containers and volumes
docker-compose down -v

# Scale services
docker-compose up --scale backend=3

# Check resource usage
docker stats
```

## 🌐 Network

Services communicate via the `smc_network` bridge network:
- Frontend → Backend: http://backend:8000
- Backend → Database: Direct filesystem access

## 💾 Data Persistence

Data is persisted in local volumes:
- Database: `./data/bot_dashboard.db`
- Logs: `./logs/`
- Config: `./config/`

Even after `docker-compose down`, data remains intact.

## 🔒 Security Notes

1. **Never commit .env file** (add to .gitignore)
2. **Change SECRET_KEY** in production
3. **Use strong passwords** for MT5 credentials
4. **Enable HTTPS** in production
5. **Restrict port access** with firewall rules

## 🎯 Development Workflow

1. Make changes to code
2. Docker automatically reloads (hot reload enabled)
3. Test changes at http://localhost:3000
4. View API docs at http://localhost:8000/docs

No need to rebuild for code changes!

## 📦 Production Build

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  backend:
    command: uvicorn backend.api:app --host 0.0.0.0 --port 8000 --workers 4
    environment:
      - LOG_LEVEL=WARNING
  
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    command: serve -s dist -l 3000
```

Build frontend for production:
```dockerfile
# frontend/Dockerfile.prod
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

Deploy:
```powershell
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

**Docker Compose makes deployment simple and consistent across environments!** 🐳
