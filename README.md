[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

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

- Docker
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

## Getting Started

### Prerequisites

- Docker; if you don’t have it yet, follow the installation instructions;
- Docker Compose; refer to the official documentation for the installation guide.
- Pre-commit; refer to the official documentation for the pre-commit.
- Cookiecutter; refer to the official GitHub repository of Cookiecutter

### Installation

#### Clone the repository

```sh
git clone git@github.com:LangCorrect/server.git
```

#### Build the Stack

This can take a while, especially the first time you run this particular command on your development system:

```sh
docker compose -f local.yml build
```

This command will also download and install the required dictionary files. We use [Fugashi](https://github.com/polm/fugashi) and [NLTK](https://www.nltk.org/) for text parsing. Fugashi parses Japanese text and NLTK parses text in various languages.

To emulate a production environment, use `production.yml` instad.

#### Run the Stack

```sh
docker compose -f local.yml up
```

The site will be accessible via <http://localhost:3000>.

#### Setup pre-commit

Make sure to setup pre-commit, otherwise there will be a bunch of CI and Linter errors.

```sh
pre-commit install
```

### Seeding Your Database

Until PR #403 gets merged, there will be no convenient way to populate the database with mock data. You'll need to manually create users, posts, prompts, and corrections.

Note: User registrations require email confirmations. Check your terminal for this link!

### Execute Management Commands

As with any shell command that we wish to run in our container, this is done using the `docker compose -f local.yml run --rm` command:

```sh
docker compose -f local.yml run --rm django python manage.py migrate
docker compose -f local.yml run --rm django python manage.py createsuperuser
```

Here, django is the target service we are executing the commands against. Also, please note that the docker exec does not work for running management commands.

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
docker compose -f local.yml run --rm django pytest #runs all tests
docker compose -f local.yml run --rm django pytest langcorrect/<app> #test specific app
```

#### Coverage

You should build your tests to provide the highest level of code coverage. You can run the pytest with code coverage by typing in the following command:

```sh
docker compose -f local.yml run --rm django coverage run -m pytest
docker compose -f local.yml run --rm django coverage report
```

#### Unit Tests

```sh
docker compose -f local.yml run --rm django python manage.py test
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
