[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

View the live website [here](https://langcorrect.com).

<div align="center">
  <a href="https://langcorrect.com" target="_blank">
    <img src="https://langcorrect.com/static/img/logo/full-logo-purple.svg" alt="Logo" height="90">
  </a>
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


## Getting Started (WIP)

### Installation

1. Clone the repository

        git clone git@github.com:LangCorrect/server.git

2. Enter the project directory and create a new virtual environment

        cd server
        $ python -m venv venv
        source venv/bin/activate

3. Install the project dependencies for local development

        $ pip install -r requirements/local.txt

4. Create the database

        createdb --username=postgres langcorrect

5. Copy and paste the `.env.example`, rename it to `.env`, and configure it

6. Install Redis

        sudo apt update && apt upgrade
        sudo apt install redis-server
        sudo service redis-server start

7. Install the fixtures

        $ python manage.py loaddata fixtures/languages.json
        $ python manage.py loaddata fixtures/correction_types.json
        $ python manage.py loaddata fixtures/tags.json

8. Load pre-commit

        $ pre-commit install


9. Start the application

        $ python manage.py runserver (starts the server)
        $ celery -A config.celery_app worker --loglevel=info (optional: for celery tasks)
        $ stripe listen --forward-to localhost:8000/subscriptions/webhook/ (optional: forwards the stripe events to the webhook endpoint, make sure to paste the signing secret `whsec_<hash>` to `STRIPE_WEBHOOK_SECRET_ENDPOINT` in `.env`)


### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

## Schema Diagram

![schema](https://github.com/LangCorrect/server/assets/115326106/279257e5-a327-439c-8190-f81064e4e147)


## Settings

This project was started with Cookiecutter Django. To see a table of configurable settings visit [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).


## Linters

        $ flake8
        $ pylint <python files that you wish to lint>

## Testing

        $ pytest
        $ python manage.py test (for unit test)
        $ mypy langcorrect (typechecks)

        $ coverage run -m pytest
        $ coverage report
        $ coverage html
        $ open htmlcov/index.html

### Celery

This app comes with Celery.

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
