[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

View the live website [here](https://langcorrect.com).

<div align="center">
  <img src="https://github.com/LangCorrect/server/assets/115326106/36c8cbe1-0611-4d0d-9b40-ca4061107699" alt="Logo" height="300">
</div>

## Introduction

Welcome to the LangCorrect repository! This community-driven platform is designed to help users master writing in foreign languages. Ideal for language learners in search of practice and native speakers willing to lend a hand, LangCorrect offers a friendly, engaging environment where you can connect, share, and learn.

This repository houses the source code for the LangCorrect web application, developed using Django for the backend and the Django templating engine for the frontend. Additionally, a React client is currently in development; you can access its repository by clicking on [LangCorrect React Client](https://github.com/LangCorrect/react-client-mui).

Interested in the features we offer or looking to contribute? Read on to find out more.

## Features

- User Registration and Authentication
- Profile Customization
- Multi-language Support
- Post Creation and Management
- Peer Review and Corrections
- Automatic Correction Syntax Highlighting
- Site and Email Notifications
- Writing Prompts
- Challenges
- Follow and Unfollow Users
- Stripe Checkout Integration
- Premium Subscription for Advanced Features
- Upload images through Local Media Storage or S3

_Note_: This is not an exhaustive list of features. LangCorrect is continually evolving, and new features are being added regularly.

## Technologies Used

- Django 4.x
- Python 3.x
- Bootstrap CSS
- HTMX
- JavaScript
- PostgreSQL
- Redis
- Celery
- SendGrid
- Stripe
- Sentry
- AWS S3 (Optional)
- CI/CD (GitHub Actions, GitLab CI, etc.)

## Roadmap

- [ ] Migrate core functionality from the oldercode base (in-progress)
- [ ] Release to production
- [ ] Re-implement DRF Views
- [ ] Resume working on the React client

## Getting Started (WIP)

### Prerequisites

### PostgreSQL

PostgreSQL is the default database for this project. If you already have it installed, skip this section. Otherwise, follow the installation steps below based on your operating system:

#### Linux

1. Install PostgreSQL and utilities

        sudo apt install -y postgresql postgresql-client-common libpq-dev

2. Start the PostgreSQL service

        sudo service postgresql start

3. Create Database and User

        sudo -u postgres createuser -s $(whoami)
        createdb

4. Verify that it installed correctly:

        psql

#### macOS (Unverified - I was not able to check this as I do not have a mac computer)

1. Install PostgreSQL and utilities

        brew install postgresql

2. Pin and Start the Service

        brew pin postgresql
        brew services start postgresql

3. Create the Database

        createdb

4. Verify that it installed correctly:

        psql

#### Troubleshooting

If you encounter the following error:

        psql: error: could not connect to server ...

Try restarting PostgreSQL:

        pg_restart

---

### Redis

Redis is used for caching and messaging brokering in this project. If you already have Redis installed, you can skip this section. Otherwise, follow the instructions based on your operating system: https://redis.io/docs/getting-started/installation/.

---

### Installation

1. Clone the repository

        git clone git@github.com:LangCorrect/server.git

1. Enter the project directory and create a new virtual environment

        cd server
        python -m venv venv
        source venv/bin/activate

1. Install the project dependencies for local development

        pip install -r requirements/local.txt

1. Create the database (if you do not have postgresql already installed there are installation instructions further down the readme)

        psql
        CREATE DATABASE langcorrect;

1. Run the migrations

        python manage.py migrate

1. Install Redis

        sudo apt update && apt upgrade
        sudo apt install redis-server
        sudo service redis-server start

1. Seed the database (view the next section)

1. Load pre-commit

        pre-commit install

1. Copy and paste the `.env.example`, rename it to `.env`, and configure it

1. Start the server

        python manage.py runserver

1. Start a celery worker (optional)

        celery -A config.celery_app worker --loglevel=info

1. Forward strip events to the webhook endpoint (optional)

        stripe listen --forward-to localhost:8000/subscriptions/webhook/

### Seeding Your Database

This project includes some sample data that you can import into your database. You have two options for doing so:

#### Option 1: Seed the Entire Database (Recommended)

This will seed your database with mock data including languages, users, posts, writing prompts, etc. Run:

        psql -d langcorrect < fixtures/seed.sql

#### Option 2: Load Only the Fixtures (Not Recommended)

If you only want to load fixtures without any mock data like posts, run:

        python manage.py loaddata fixtures/languages.json
        python manage.py loaddata fixtures/correction_types.json

### Setting Up Your Users

#### Pre-seeded

For your convenience, the database comes pre-seeded with some basic user accounts. You can use these credentials to log in and explore the application.

| id | username | password | email | role | description |
| - | - | - | - | - | - |
| 1 | admin | password | admin@dundermifflin.com | staff | Use this to access the admin dashboard |
| 2 | michael | password | mscott@dundermifflin.com | Premium | Use this to test out premium functionality |
| 3 | jim | password | jim@dundermifflin.com | member | Use this for standard member access |
| 4 | pam | password | pbeesly@dundermifflin.com | member | Use this for standard member access |
| 5 | dwight | password | dschrute@dundermifflin.com | member | Use this for standard member access |


#### Creating New Accounts

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      python manage.py createsuperuser

## Schema Diagram

![schema](https://github.com/LangCorrect/server/blob/main/schema.png)

## Settings

This project was started with Cookiecutter Django. To see a table of configurable settings visit [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Linters and Testing

This project uses several tools to maintain code quality. Below are the commands to run these tools.

### Linters

We use `flake8` for checking Python code for style and syntax errors and `pylint` for additional code analysis.

- Run `flake8` to check the entire project for PEP8 compliance
- Run `pylint <python files that you wish to lint>` to perform static code analysis

### Testing

We use `pytest` for our testing needs and `mypy` for type checking. Code coverage reports are generated using `coverage`.

Run the test suite:

        pytest

Run Django unit tests:

        python manage.py test (for unit test)

Performing type checks on the codebase:

        mypy langcorrect

To run code coverage and generate reports:

        coverage run -m pytest
        coverage report
        coverage html
        open htmlcov/index.html

### Celery

This app utilizes Celery as an asynchronous task queue to efficiently manage background tasks, such as updating user rankings and running periodic tasks via the Beat scheduler.

To run a celery worker:

```bash
cd langcorrect
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd langcorrect
celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd langcorrect
celery -A config.celery_app worker -B -l info
```

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

### Contributing to LangCorrect

We welcome contributions from everyone, whether you are a seasoned programmer or a first-timer. Below are the steps and guidelines you should follow to contribute to this project.

Please make sure that you have:

1. Set up the project and have it running locally. Follow the instructions in the Getting Started section.
2. Familiarized yourself with our Code of Conduct (TBD).

Contribution Workflow:

1. **Find an Issue:** Browse the open issues and comment on one expressing your intent to work on that issue.
2. **New Issue:** If you've found a new issue or have a new feature to suggest, create a new issue to report it.
3. **Fork & Clone:** Fork the project to your own GitHub account, and clone it to your local machine.
4. **Create a Feature Branch:** Create a new branch named after the issue you are solving, Prefix the branch name with the issue number: `git checkout -b 154-fixing-some-issue`.
5. **Make Changes:** Implement your changes.
6. **Run pre-commit Checks:** Before commiting, run pre-commit checks to ensure code style and quality: `pre-commit`.
7. **Commit Changes:** Commit your changes with a meaningful commit message, referencing the issue number: `git commit -m "Add meaningful description here (#154)"`
8. **Push Changes**: Push your changes.
9. **Open Pull Request:** Open a PR in the original repository and fill in the PR template.
10. **Address Reviews:** Maintainers will review your PR. Make any requested changes if needed.

If you have any questions or need further clarification on any of the steps, feel free to reach out to our Discord: https://discord.gg/Vk7KcV26Fe.

We look forward to your contributions!
