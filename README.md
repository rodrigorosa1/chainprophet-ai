# ChainProphet AI

FastAPI service for ChainProphet forecasting workflows. The service exposes
user, authentication, subscription, account, forecast, and analysis endpoints,
and runs scheduled jobs for model training, forecast generation, and forecast
analysis.

## Requirements

- Docker
- Docker Compose
- A configured `.env` file in the project root

## Environment

Create a `.env` file in the project root before starting the containers. The
Docker Compose setup loads this file into the `ai` service.

Required keys:

```env
PYTHON_VERSION=3.12
APP_NAME=ChainProphet AI
PORT=8000
DEBUG=true
DATABASE_URL=postgresql://user:password@host.docker.internal:5432/database
APPLICATION_URL=http://localhost
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
OPENAI_TIMEOUT_SECONDS=60
SECRET_KEY=replace_with_a_secure_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=3600
TIMEZONE=America/Sao_Paulo
POOL_RECYCLE=3600
```

Use `host.docker.internal` in `DATABASE_URL` when the database runs on the host
machine. If the database runs in another Docker service or remote host, use that
host name instead.

## Run With Docker Compose

Build and start the application:

```bash
docker compose up --build -d
```

Follow logs:

```bash
docker compose logs -f ai
```

Stop the stack:

```bash
docker compose down
```

Restart only the API service:

```bash
docker compose restart ai
```

Rebuild after dependency changes:

```bash
docker compose build --no-cache ai
docker compose up -d
```

## Services

The Compose stack defines two services:

- `ai`: FastAPI application built from `infra/Dockerfile` and started with
  `python main.py`.
- `webserver`: Nginx reverse proxy that forwards requests to `ai:8000`.

Nginx publishes ports `80` and `443`. The local FastAPI app runs inside Docker
on port `8000`; external access should go through Nginx unless you add a direct
port mapping for the `ai` service.

## HTTPS Certificates

The Nginx service mounts certificates from `infra/certs`:

```text
infra/certs/appfollowup.pem
infra/certs/appfollowup.key
```

For local development, either provide compatible certificate files or adjust
`infra/nginx/nginx.conf` to use only HTTP.

## Useful Commands

Open a shell in the API container:

```bash
docker compose exec ai bash
```

Run tests inside the API container:

```bash
docker compose exec ai python -m pytest -q
```

Run database migrations:

```bash
docker compose exec ai alembic upgrade head
```

Run analysis commands manually:

```bash
docker compose exec ai python -m app.commands.analysis.run_train_models
docker compose exec ai python -m app.commands.analysis.run_forecast_prices
docker compose exec ai python -m app.commands.analysis.run_full_analysis_cycle
```

## API

When the stack is running, the API is available through the Nginx service:

- HTTP: `http://localhost`
- HTTPS: `https://localhost` when certificates are configured

FastAPI documentation is available at:

- `http://localhost/docs`
- `http://localhost/redoc`

## Scheduled Jobs

The application starts these recurring jobs on FastAPI startup:

- Train ML models every 12 hours.
- Generate forecasts every hour, after the first wait interval.
- Run the full analysis cycle every 24 hours, after the first wait interval.

Set `DEBUG=false` in production-like environments unless live reload is needed.
