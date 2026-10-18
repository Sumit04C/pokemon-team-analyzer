10-17-2026: Initial commit and MVP developed using AI. 

Function: logging teams for playthroughs of different games for generations 1-3. 

Tools:
- Python
- Docker
- PostgreSQL

Next Steps:
1. Clean up the UX/UI design: color-coding the different types. 
2. Security: upgrading different dependencies and implementing account creation and MFA. 
3. Figuring out a way to include data for games Gens 4-9. 
4. Adding in pngs of the different Pokemon in each of their slots. 




# PokéDash

Record the teams you used in your Pokémon playthroughs and explore them on a dashboard: total playthroughs, most-played generation, most common types, and most-used Pokémon.

**Stack:** Streamlit (UI), PostgreSQL (data), Docker Compose (runs both), PokéAPI (reference data).

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Docker Compose v2). Open it and wait for it to finish starting before running any commands.
- [Git](https://git-scm.com/)

You do **not** need to install Python or any packages yourself. Docker handles all dependencies.

Check that Compose is available:

```bash
docker compose version
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Sumit04C/pokemon-team-analyzer
cd pokemon-team-analyzer
```

### 2. Create your `.env` file

The database credentials live in a `.env` file that is not committed to git. Copy the example and choose your own values:

```bash
cp .env.example .env
```

Then edit `.env`:

```
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

Use letters, numbers, and dashes in the password. Characters like `@`, `:`, `/`, and `#` break the database connection URL.

Confirm the values are being read:

```bash
docker compose config | grep POSTGRES
```

You should see your username and password filled in, not blanks.

### 3. Start the database

```bash
docker compose up -d db
```

On first start, Postgres runs the SQL files in `db/init/` to create the tables. Wait about 10 seconds, then check:

```bash
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -P pager=off -c "\dt"'
```

You should see tables including `generations`, `types`, `games`, `pokemon`, `playthroughs`, and `team_members`.

### 4. Load the reference data from PokéAPI

```bash
docker compose run --rm app python scripts/load_pokeapi.py
```

This fetches generations, types, and Pokémon. The first run takes a few minutes. Responses are cached in `app/scripts/.cache`, so re-runs are fast. The script is safe to run more than once.

### 5. Add the games

The games list isn't loaded from PokéAPI. Add them once (running this twice creates duplicates):

```bash
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
INSERT INTO games (name, generation_id) VALUES
(\$\$Red\$\$, 1), (\$\$Blue\$\$, 1), (\$\$Yellow\$\$, 1),
(\$\$Gold\$\$, 2), (\$\$Silver\$\$, 2), (\$\$Crystal\$\$, 2),
(\$\$Ruby\$\$, 3), (\$\$Sapphire\$\$, 3), (\$\$Emerald\$\$, 3),
(\$\$FireRed\$\$, 3), (\$\$LeafGreen\$\$, 3);"'
```

Add more rows for later generations as needed. Generation IDs 1 through 9 match PokéAPI's numbering.

### 6. Start the app

```bash
docker compose up --build
```

Open <http://localhost:8501>.

## Using the app

1. Open **Add Playthrough** in the sidebar.
2. Enter a player name, choose a game, pick six Pokémon (the dropdowns are type-to-search), and save.
3. Return to the main **Dashboard** page to see the charts.

The dashboard is empty until at least one playthrough is saved.

## Everyday commands

| Task | Command |
| --- | --- |
| Start everything | `docker compose up` |
| Start in the background | `docker compose up -d` |
| Stop everything | `docker compose down` |
| Rebuild after changing `requirements.txt` | `docker compose build app` |
| View database logs | `docker compose logs db` |
| Reset the database (deletes all data) | `docker compose down -v` |

Code changes in `app/` are picked up automatically without a rebuild. Streamlit shows a "Rerun" prompt in the browser.

## Troubleshooting

**`Database is uninitialized and superuser password is not specified`**
Compose isn't reading your `.env`. Make sure it is named exactly `.env`, sits next to `docker-compose.yml`, and has no spaces around the `=`. Then run `docker compose down -v` and start again.

**Tables are missing**
Init scripts in `db/init/` only run the first time the database volume is created. Reset with `docker compose down -v`, then `docker compose up -d db`.

**`ModuleNotFoundError` when running a script**
Rebuild the image: `docker compose build --no-cache app`.

**`database "..." does not exist`**
The database name in `docker-compose.yml` (`POSTGRES_DB` and the end of `DATABASE_URL`) must match, and changing it requires resetting the volume with `docker compose down -v`.

**Port 5432 or 8501 already in use**
Another program is using the port. Change the left side of the port mapping in `docker-compose.yml` (for example `"5433:5432"`).

**`docker compose` is not recognized**
Update Docker Desktop, or make sure it is running.

## Project structure

```
.
├── docker-compose.yml
├── .env.example          # copy to .env and fill in
├── db/init/              # SQL that creates the schema on first start
└── app/
    ├── Dockerfile
    ├── requirements.txt
    ├── db.py             # database connection and cached queries
    ├── Dashboard.py      # main dashboard page
    ├── pages/            # additional Streamlit pages (data entry)
    └── scripts/
        └── load_pokeapi.py
```

## Notes

- Alternate forms (Mega evolutions, regional variants) are stored as separate Pokémon, matching PokéAPI.
- Dual-type Pokémon count toward both of their types in the "most common types" chart.
- Never commit `.env`. It is listed in `.gitignore`.
