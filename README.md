[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

View the live website [here](https://langcorrect.com).

<div align="center">
  <img src="https://github.com/LangCorrect/server/assets/115326106/36c8cbe1-0611-4d0d-9b40-ca4061107699" alt="Logo" width="350">
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

## Folder Structure (WIP)

```
langcorrect/ - Project-specific code
    constants/ - Project-wide constants
    helpers/ - Project-wide helpers
    templates/ - All project templates
    static/ - All project static files
    <app>/ - Specific app folders
        constants/ - App-specific constants
        helpers/ - App-specific helpers
        api/ - wip App-specific API files
```

## Road Map (WIP)

- [x] Update DB Schema for more efficient queries and organization
- [x] Migrate data and codebase to use new DB schema
- [] Release API
- [] Release Next.js client
- [] Release Messenger
- [] Remove deprecated project templates
- [] Containerize project (again...)
- [] Work on getting test coverage ~80%

## Getting Started

### Prerequisites

- PostgreSQL; refer to the official documentation for installation.
- Pre-commit; refer to the official documentation for the pre-commit.
- Cookiecutter; refer to the official GitHub repository of Cookiecutter

### Installation

#### Clone the repository

```sh
git clone git@github.com:LangCorrect/server.git
```

#### Create and activate a virtual environment

```sh
python3 -m venv venv
source venv/bin/activate
```

#### Install project dependencies

```sh
pip install -r requirements/local.txt
```

#### Install dictionaries

We use [Fugashi](https://github.com/polm/fugashi) and [NLTK](https://www.nltk.org/) for text parsing. Fugashi parses Japanese text and NLTK parses text in various languages.

```sh
python -m unidic download
python -m nltk.downloader popular
```

#### Create the database

```sh
psql
CREATE DATABASE langcorrect;
```

#### Run the migrations

```sh
python manage.py migrate
```

#### Setup pre-commit

Make sure to setup pre-commit, otherwise there will be a bunch of CI and Linter errors.

```sh
pre-commit install
```

#### Install fixtures

```sh
python manage.py loaddata fixtures/languages.json
python manage.py loaddata fixtures/correction_types.json
```

#### Run the server

```sh
python manage.py runserver
```

The site will be accessible via <http://localhost:8000>.

Note: User registrations require email confirmations. Check your terminal for this link!

#### Start a celery worker (optional)

```sh
celery -A config.celery_app worker --loglevel=info
```

#### Forward Stripe events to the webhook endpoint (optional)

```sh
stripe listen --forward-to localhost:8000/subscriptions/webhook/
```

## Settings

This project was started with Cookiecutter Django. To see a table of configurable settings visit [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Linters and Testing

This project uses several tools to maintain code quality. Below are the commands to run these tools.

### Linters

We use `flake8` for checking Python code for style and syntax errors and `pylint` for additional code analysis.

- Run `flake8` to check the entire project for PEP8 compliance
- Run `pylint <python files that you wish to lint>` to perform static code analysis

### Testing

#### Pytest

This project uses the [Pytest](https://docs.pytest.org/en/latest/example/simple.html), a framework for easily building simple and scalable tests.

```sh
python manage.py pytest #runs all tests
python manage.py pytest langcorrect/<app> #test specific app
```

#### Coverage

You should build your tests to provide the highest level of code coverage. You can run the pytest with code coverage by typing in the following command:

```sh
python manage.py coverage run -m pytest
python manage.py coverage report
```

#### Unit Tests

```sh
python manage.py test
```

#### Forward strip events to the webhook endpoint (optional)

```sh
stripe listen --forward-to localhost:8000/subscriptions/webhook/
```

#### Celery

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

If you have any questions or need further clarification on any of the steps, feel free to reach out to our Discord: <https://discord.gg/Vk7KcV26Fe>.

We look forward to your contributions!
