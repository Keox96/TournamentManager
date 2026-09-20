# TournamentManager

TournamentManager is a Python 3.13+ application for managing competitive
 tournaments. It exposes an asynchronous REST API built with FastAPI and uses
 PostgreSQL through SQLAlchemy and Alembic.

The application is organized around a hexagonal architecture:
- `src/domain/`: entities, business rules, services, repository ports and
  domain exceptions.
- `src/api/`: FastAPI application, versioned routes, schemas, dependencies and
  exception handlers.
- `src/infrastructure/`: SQLAlchemy models, database session and repository
  adapters.
- `discord_bot/`: Discord integration entry point.
- `migrations/`: Alembic migration history.

## Features

### Players

- Create, retrieve, update and delete players.
- Store username, display name, email and icon URL.
- List players with pagination, full-text-like search and filters for username,
  display name, email and creation dates.
- Sort by creation date, username, display name or email.
- Include team memberships and assigned roles in responses.

### Teams and memberships

- Create, retrieve, update and delete teams.
- Store a team name, a 2-5 character alphanumeric tag, logo URL and
  description.
- List teams with pagination, search, creation-date filters and sorting by
  name, tag or creation date.
- Add, update and remove players from teams.
- Support the roles `player`, `captain` and `substitute`.
- Prevent duplicate memberships and enforce team/player and membership
  business rules.

### Tournaments

- Create, retrieve, update and delete tournaments.
- Configure the guild, game, team limit, minimum players per team,
  description and optional best-of value.
- Register and remove teams from a tournament.
- Prevent duplicate registrations, full tournaments, teams with too few
  players and players registered through multiple teams in one tournament.
- List tournaments with pagination, search, filters and sorting.
- Filter by guild, status, mode, game, name, team limits, minimum team size
  and date ranges.

Supported tournament modes:

- `single_elimination`
- `double_elimination`
- `round_robin`
- `swiss`

Supported tournament statuses are `draft`, `open`, `in_progress`,
`completed` and `cancelled`. The implemented workflow is:

```text
draft -> open -> in_progress -> completed
```

The API currently exposes operations for opening and starting tournaments;
there is no dedicated cancellation endpoint.

### Matches and results

- Generate matches when a tournament starts according to its selected mode.
- Retrieve all matches for a tournament or only the next playable matches.
- Retrieve an individual match.
- Record a match result with team scores and per-player statistics.
- Store team score, kills, deaths, assists and rank.
- Store player score, kills, deaths and assists.
- Reject incomplete or inconsistent result payloads.
- Reject draws in elimination matches.
- Generate the next elimination round when the current round is complete.
- Complete the tournament when all its matches are completed.

Match statuses are `pending`, `in_progress`, `completed` and `cancelled`.

### Ranking

The domain ranking service calculates standings for completed matches and
supports:

- elimination ranking with winner and elimination-round placement;
- round-robin ranking using points, head-to-head points, score difference and
  score for;
- Swiss ranking using points, Buchholz, Sonneborn-Berger, score difference and
  score for.

### API platform

- FastAPI OpenAPI documentation at `/docs` and `/redoc`.
- API prefix: `/api/v1`.
- Pydantic request and response validation.
- Consistent handling of domain errors and request validation errors.
- Pagination with `page` and `size` query parameters (`size` is limited to
  100).
- Sort syntax such as `?sort=name:asc&sort=created_at:desc`.
- CORS is enabled for all origins, methods and headers in the current
  configuration.
- No authentication or authorization layer is currently implemented.

## API endpoints

All routes below are prefixed with `/api/v1`.

| Resource | Method | Path | Purpose |
| --- | --- | --- | --- |
| Players | GET | `/players/` | Paginated list with filters, search and sorting |
| Players | GET | `/players/{player_id}` | Retrieve a player |
| Players | POST | `/players/` | Create a player |
| Players | PUT | `/players/{player_id}` | Update a player |
| Players | DELETE | `/players/{player_id}` | Delete a player |
| Teams | GET | `/teams/` | Paginated list with filters, search and sorting |
| Teams | GET | `/teams/{team_id}` | Retrieve a team |
| Teams | POST | `/teams/` | Create a team |
| Teams | PUT | `/teams/{team_id}` | Update a team |
| Teams | DELETE | `/teams/{team_id}` | Delete a team |
| Team members | POST | `/teams/members` | Add a player to a team |
| Team members | PUT | `/teams/{team_id}/members/{player_id}` | Change a member role |
| Team members | DELETE | `/teams/{team_id}/members/{player_id}` | Remove a member |
| Tournaments | GET | `/tournaments/` | Paginated list with filters, search and sorting |
| Tournaments | GET | `/tournaments/{tournament_id}` | Retrieve a tournament |
| Tournaments | POST | `/tournaments/` | Create a tournament |
| Tournaments | PUT | `/tournaments/{tournament_id}` | Update a tournament |
| Tournaments | DELETE | `/tournaments/{tournament_id}` | Delete a tournament |
| Tournaments | POST | `/tournaments/{tournament_id}/open` | Open registration |
| Tournaments | POST | `/tournaments/{tournament_id}/start` | Start the tournament and generate matches |
| Tournament teams | POST | `/tournaments/teams` | Register a team |
| Tournament teams | DELETE | `/tournaments/{tournament_id}/teams/{team_id}` | Remove a registered team |
| Matches | GET | `/matchs/tournament/{tournament_id}` | List tournament matches |
| Matches | GET | `/matchs/tournament/{tournament_id}/next` | List currently playable matches |
| Matches | GET | `/matchs/{match_id}` | Retrieve a match |
| Matches | PUT | `/matchs/{match_id}/result` | Submit a match result |

The `/matchs` spelling is kept for compatibility with the existing API.

## Persistence and migrations

The infrastructure layer provides SQLAlchemy repositories for players, teams,
tournaments, tournament memberships, matches, match teams and player
performances. The application uses PostgreSQL and Alembic migrations.

The API opens the database connection pool during application startup and
closes it during shutdown. The default connection pool settings are 2 minimum
connections, 10 maximum connections and a 30 second timeout.

## Configuration

Settings are loaded from `.env` when present. Important variables include:

| Variable | Default |
| --- | --- |
| `APP_NAME` | `TournamentManager API` |
| `APP_ENV` | `development` |
| `LOG_LEVEL` | `INFO` |
| `API_HOST` | `0.0.0.0` |
| `API_PORT` | `8000` |
| `API_DEBUG` | `false` |
| `DATABASE_URL` | Built from the PostgreSQL variables below |
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `tournament_db` |
| `POSTGRES_USER` | `tournament_user` |
| `POSTGRES_PASSWORD` | `tournament_pass` |
| `DB_POOL_MIN` | `2` |
| `DB_POOL_MAX` | `10` |
| `DB_POOL_TIMEOUT` | `30` |
| `SECRET_KEY` | `dev-secret-key-change-in-prod` |
| `DISCORD_TOKEN` | Empty |
| `DISCORD_GUILD_ID` | Empty |

## Installation

### Prerequisites

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL, or Docker and Docker Compose

Install the project and development dependencies:

```bash
uv sync
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Start the API locally:

```bash
uv run uvicorn src.api.app:app --reload
```

The API is then available at `http://localhost:8000`.

### Docker Compose

Start the application stack:

```bash
docker compose up --build
```

The compose configuration includes the API, PostgreSQL and pgAdmin services.

## Discord bot

The repository contains a Discord bot entry point in
`discord_bot/bot.py`. Configure `DISCORD_TOKEN` and `DISCORD_GUILD_ID` before
starting it:

```bash
uv run python discord_bot/bot.py
```

The REST API remains the authoritative interface for the domain features
listed above.

## Development commands

Run the test suite:

```bash
uv run pytest
```

Run linting and type checking:

```bash
uv run ruff check src/
uv run mypy src/
```

Tests are divided into unit tests and integration tests under `tests/`.
Postman collections and environments are available under `postman/`.

## Current scope

The `src/api/v1/stats/` package currently contains only module and schema
placeholders; no statistics route is registered in the FastAPI application.
Authentication, authorization and a dedicated tournament cancellation API are
also outside the current implementation.
# TournamentManager

TournamentManager is a sports tournament management application developed in Python, using hexagonal architecture (ports and adapters) to ensure a clear separation between business logic and external interfaces. This project allows managing players, teams, tournaments, and matches, with a REST API, an integrated Discord bot, and easy deployment via Docker.

## Architecture

The project follows hexagonal architecture (Hexagonal Architecture), also known as Ports and Adapters. This approach organizes the code around the business domain at the center, isolated from external concerns:

- **Domain** : Contains business entities, services, abstract repositories, and business rules. This is the core of the application, independent of external technologies.
  - `entities/` : Defines entities like `Player`, `Team`, `Tournament`, `Match`.
  - `services/` : Business logic for CRUD operations and specific rules.
  - `repositories/` : Abstract interfaces for data access.
  - `exceptions/` : Business error handling.
  - `utils/` : Utilities like enums and bracket generation.

- **Infrastructure** : Implements adapters for external technologies (database, external APIs, etc.).
  - `database/` : SQLAlchemy models, database session, concrete repositories.

- **API** : User interface and integration layer.
  - `v1/` : REST endpoints for players, teams, tournaments, statistics.
  - Exception handling and dependencies.

- **Discord Bot** : Integration to interact with Discord.

This architecture ensures testability, maintainability, and scalability by allowing adapter changes without touching the domain.

## Features

### Player Management
- Create, read, update, and delete players.
- Each player has a unique username.
- Participation in teams and tournaments.

### Team Management
- Create, read, update, and delete teams.
- Each team has a unique name and tag (2-5 alphanumeric characters).
- Optional logo URL and description.
- List teams with advanced filtering (by name, tag, creation date), sorting (by name, tag, creation date), pagination, and search.
- Team members management with roles (captain, member) and statistics (rank, score).
- Team statistics (wins, losses, etc.).
- Integration with tournaments and matches.

### Tournament Management
- Create tournaments with different modes (single elimination, round-robin, etc.).
- Tournament statuses: draft, open, ongoing, finished.
- Team registration for tournaments.
- Automatic bracket generation for final phases.
- Rankings and team scores.

### Match Management
- Organize matches between teams in a tournament.
- Track scores, match statuses (scheduled, ongoing, finished).
- Detailed results for each participating team.

### REST API
- Endpoints for all CRUD operations on entities.
- Pagination, filters, and sorting for lists.
- Error handling with specific error codes.
- Automatic documentation via FastAPI.

### Discord Bot
- Integration with Discord to announce tournaments, results, etc.
- Commands to interact with the system from Discord.

### Statistics
- Calculation and display of player and team statistics.
- Global rankings.

### Database
- Use of PostgreSQL with SQLAlchemy for ORM.
- Automated migrations with Alembic.
- Relational schema to manage entity relationships.

### Tests
- Unit tests for services and utilities.
- Integration tests for API endpoints.
- Use of Pytest with asyncio for asynchronous tests.

### Deployment
- Docker configuration for the application, database, and pgAdmin.
- docker-compose to orchestrate services.
- Development and production environments.

## Installation

### Prerequisites
- Python 3.13+
- Docker and Docker Compose
- UV (Python package manager)

### Local Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd TournamentManager
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Configure the database (see Configuration section).

4. Run the application:
   ```bash
   uv run uvicorn src.api.app:app --reload
   ```

### With Docker
1. Copy the `.env.example` file to `.env` and configure the variables.
2. Start the services:
   ```bash
   docker-compose up --build
   ```

## Configuration

- Environment variables in `.env`:
  - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: For the database.
  - `DISCORD_TOKEN`: For the Discord bot.
  - Other settings in `src/config.py`.

## Usage

### API
- Access API documentation: `http://localhost:8000/docs`
- Request examples in the `postman/` folder.

### Discord Bot
- Configure the token and run the bot:
  ```bash
  uv run python discord_bot/bot.py
  ```

## Tests

Run tests:
```bash
uv run pytest
```

## Contribution

- Use Ruff for linting.
- MyPy for type checking.
- Respect hexagonal architecture when adding features.

## License

[To be defined]