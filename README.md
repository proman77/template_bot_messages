
# Aiogram 3 Bot Template

This is a template for telegram bots written in python using the `aiogram` framework


You can learn how to develop telegram bots using the `aiogram` framework in the following courses (in Russian):
1. <a href="https://stepik.org/course/120924/">Телеграм-боты на Python и AIOgram</a>
2. <a href="https://stepik.org/a/153850?utm_source=kmsint_github">Телеграм-боты на Python: продвинутый уровень</a>

## About the template

### Used technology
* Python 3.12;
* aiogram 3.x (Asynchronous Telegram Bot framework);
* aiogram_dialog (GUI framework for telegram bot);
* dynaconf (Configuration Management for Python);
* taskiq (Async Distributed Task Manager);
* fluentogram (Internationalization tool in the Fluent paradigm);
* Docker and Docker Compose (containerization);
* PostgreSQL (database);
* NATS (queue and FSM storage);
* Redis (cache, taskiq result backend);
* Alembic (database migrations with raw SQL).

### Structure

```
📁 aiogram_bot_template/
├── 📁 alembic/          # Database migrations
├── 📁 app/              # Main application logic
│   ├── 📁 bot/          # Bot handlers, dialogs, middlewares
│   ├── 📁 infrastructure/ # DB, Cache, NATS connections
│   └── 📁 services/     # Business logic and background tasks
├── 📁 config/           # Configuration files
├── 📁 docs/             # Documentation and development steps
│   └── 📄 DATABASE_SCHEMA.md # Detailed database schema description
├── 📁 locales/          # Localization files (Fluent)
├── 📁 logs/             # Application logs
├── 📁 nats_broker/      # NATS configuration and migrations
├── 📁 tools/            # Utility and debug scripts
├── 📁 win_fix/          # Windows-specific fixes
├── .env                 # Environment variables (local)
├── alembic.ini          # Alembic configuration
├── docker-compose.yml   # Docker orchestration
├── main.py              # Entry point
├── pyproject.toml       # Project dependencies (uv/pip)
├── run_worker.bat       # Windows worker runner
└── uv.lock              # Dependency lock file
```

## Installation

1. Clone the repository to your local machine via HTTPS:

```bash
git clone https://github.com/kmsint/aiogram_bot_template.git
```
or via SSH:
```bash
git clone git@github.com:kmsint/aiogram_bot_template.git
```

2. Create a `docker-compose.yml` file in the root of the project and copy the code from the `docker-compose.example` file into it.

3. Create a `.env` file in the root of the project and copy the code from the `.env.example` file into it. Replace the required secrets (BOT_TOKEN, ADMINS_CHAT, etc).

4. Run `docker-compose.yml` with `docker compose up` command. You need docker and docker-compose installed on your local machine.

5. Create a virtual environment in the project root and activate it.

6. Install the required libraries in the virtual environment. With `pip`:
```bash
pip install .
```
or if you use `poetry`:
```bash
poetry install --no-root
```
7. Write SQL code in the `upgrade` and `downgrade` functions to create a database schema. See example in file `alembic/versions/1541bb8a3f26_.py`.

8. If required, create additional empty migrations with the command:
```bash
alembic revision
```
and fill them with SQL code.

9. Apply database migrations using the command:
```bash
alembic upgrade head
```

10. Run `create_stream.py` to create NATS stream for delayed messages service:
```bash
python3 -m nats_broker.migrations.create_stream
```

11. If you want to use the Taskiq broker for background tasks as well as the Taskiq scheduler, add your tasks to the `tasks.py` module and start the worker first:
```bash
taskiq worker app.services.scheduler.taskiq_broker:broker -fsd
```
and then the scheduler:
```bash
taskiq scheduler app.services.scheduler.taskiq_broker:scheduler
```

12. Run `main.py` to check the functionality of the template.

13. You can fill the template with the functionality you need.

## Developer tools

For convenient interaction with nats-server you need to install nats cli tool. For macOS you can do this through the homebrew package manager. Run the commands:
```bash
brew tap nats-io/nats-tools
brew install nats-io/nats-tools/nats
```
For linux:
```bash
curl -sf https://binaries.nats.dev/nats-io/natscli/nats@latest | sh
sudo mv nats /usr/local/bin/
```
After this you can check the NATS version with the command:
```bash
nats --version
```

## Mailing Service (Broadcast)

The template includes a built-in mailing service that allows administrators to send messages to bot users based on their language.

### Features
- **Language Targeting**: Send messages to users of a specific language (RU, EN) or to everyone.
- **Multi-content Support**: Supports text, photos, videos, animations, and documents.
- **Real-time Monitoring**: Track progress, successful deliveries, and errors.
- **Control**: Pause, resume, or stop the broadcast at any time.
- **Robustness**: Automatically handles rate limits and identifies users who have blocked the bot.

### How to use
1. **Start the Broadcast**: Send the `/broadcast` command (available only to `ADMIN` or `OWNER`).
2. **Select Language**: Choose the target audience language.
3. **Input Message**: Send or forward the message you want to broadcast.
4. **Preview**: Check how the message looks and confirm the settings.
5. **Launch**: Click "✅ Запустить рассылку" to start the process.
6. **Monitor**: You will be redirected to a monitoring window where you can see the progress and control the broadcast.

### Requirements
To use the mailing service, ensure that the **Taskiq worker** is running:
```bash
taskiq worker app.services.scheduler.taskiq_broker:broker -fsd
```

#### ⚠️ Windows Note
On Windows, the default `ProactorEventLoop` may cause issues with Taskiq and NATS. To fix this, use the provided batch script which forces the use of `SelectorEventLoop`:
```bash
run_worker.bat
```
This script sets the `PYTHONPATH` to include a fix located in the `win_fix` directory.

## TODO

1. Set up a CICD pipeline using Docker and GitHub Actions