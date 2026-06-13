# Deployment Guide

## AWS ECS + Cloudflare (Production)

### 1. Build & push Docker images

```bash
# Backend
docker build -t livescore-api ./backend
docker tag livescore-api:latest <ECR_URI>/livescore-api:latest
docker push <ECR_URI>/livescore-api:latest

# Frontend (build static files first)
cd frontend && npm run build
docker build -t livescore-frontend .
docker push <ECR_URI>/livescore-frontend:latest
```

### 2. AWS Resources needed
- ECS Cluster (Fargate)
- RDS Aurora PostgreSQL (Multi-AZ)
- ElastiCache Redis (Cluster mode)
- ALB (Application Load Balancer)
- ECR (Elastic Container Registry)
- SSM Parameter Store (for secrets)
- S3 bucket (for static assets / logos)
- CloudFront or Cloudflare CDN

### 3. ECS Task Definitions
Create two tasks:
- `livescore-api` — Flask gunicorn server
- `livescore-worker` — Celery worker + beat

### 4. Environment Variables (SSM)
Store all secrets in AWS SSM Parameter Store:
```
/livescore/prod/SPORTRADAR_KEY
/livescore/prod/APIFOOTBALL_KEY
/livescore/prod/DATABASE_URL
/livescore/prod/REDIS_URL
/livescore/prod/SECRET_KEY
```

### 5. Cloudflare Setup
- Proxy DNS through Cloudflare
- Enable caching for static assets (Cache-Control: immutable)
- Set up Page Rules:
  - `/api/*` → Cache Level: Bypass
  - `/assets/*` → Cache Level: Cache Everything, Edge TTL: 1 month
  - `/` → Cache Level: Standard, Browser TTL: 30s

### 6. Auto-scaling
ECS Service auto-scaling policy:
- Scale out: CPU > 60% for 2 minutes
- Scale in: CPU < 30% for 10 minutes
- Min: 2 tasks, Max: 20 tasks

### 7. World Cup / Peak traffic preparation
Run before major tournaments:
```bash
# Pre-warm cache
python -c "from app.tasks.poller import poll_live_scores; poll_live_scores.apply()"

# Scale ECS manually
aws ecs update-service --cluster livescore --service livescore-api --desired-count 10
```

## GitHub Actions CI/CD

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Build and push to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
          docker build -t livescore-api ./backend
          docker push $ECR_URI/livescore-api:latest
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster livescore --service livescore-api --force-new-deployment
```
