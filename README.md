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