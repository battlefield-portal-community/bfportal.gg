# Contributing to bfportal.gg

First off, thanks for taking the time to contribute! 🎉🎉

This file contains a few guidelines on how to contribute to the Battlefield Portal Library hosted at bfportal.gg
These are not rules but just some suggestion, so feel free to propose any change in the project

## Architecture of the Project

Before you start contributing you should understand the stack that this projects uses

![image](https://i.imgur.com/INghzbZ.png)

As shown in the architecture picture the project is built based on the following:

**Backend:**

- [Python](https://www.python.org/downloads/)
  - [wagtail](https://docs.wagtail.org/en/stable/getting_started/tutorial.html)
  - [django](https://docs.djangoproject.com/en/4.1/intro/tutorial01/)
- [PostgreSQL](https://www.postgresql.org/)

**Frontend:**

- HTML/CSS/JS
  - Django Templates
  - NPM JS Libraries
  - [tailwindcss](https://github.com/tailwindlabs/tailwindcss)

**Runtime Environment:**

- [Docker](https://www.docker.com) Container Images on Linux

If you're not familiar with Django or Wagtail, it might be good to start with [wagtail](https://docs.wagtail.org/en/stable/getting_started/tutorial.html).

### Django Apps

| App      | Description                                                                                                            |
| -------- | ---------------------------------------------------------------------------------------------------------------------- |
| bfportal | This app Contains the base settings and base html file that is used to generate any webpage on the website             |
| core     | The app is the heart of "Experience listing" and User profile, all the models used in the Database are defined in this |

### Few key components

- All the "webpages" are in `<app>/<templates>/<app>/` directory, we can use this structure to override the template of other apps that are installed in python
- The models for all "pages" type are defined in [`/core/models/*`](/bfportal/core/models)
- The API at (https://api.bfportal.gg/) is defined and controlled by [`/core/api/*`](/bfportal/core/api)
- Form validation and discord hooks are done in [`/core/views.py`](/bfportal/core/views.py)

# How to contribute

- Pick an [issue](https://github.com/battlefield-portal-community/bfportal.gg/issues) or Create a new one explaning the change/feature you want to add
- Create a new branch for that issue
- Make your changes
- Make sure all the precommit test are passed
- Open a pull request to merge the branch into main branch
- The changes will be reviewed on dev deployment
- Upon successfully testing dev will be merged into production

## Use of AI

We do **not** write the code for this project using AI — every line is written by hand by a human contributor. AI assistants (e.g. Claude Code) are permitted only for the narrow set of tasks below:

- **Discussing the approach in plan mode.** The assistant helps talk through structure, DB schema, relationships, and trade-offs, and points at the existing files a change would touch. It does **not** produce an implementation checklist, write diffs, or hand off a plan to execute — the contributor implements everything by hand. The rules for this live in [`CLAUDE.md`](/CLAUDE.md).
- **The workflow skills defined in [`.claude/skills/`](/.claude/skills).** These are the only sanctioned automations:
  - `plan-issue` — turn an agreed plan into well-formed GitHub issue(s) and cut a feature branch, run before any code is written.
  - `open-pr` — open a pull request for a feature branch and link all the issues it closes.

Using AI to generate the actual code, tests, migrations, or templates is **not** accepted. If you're unsure whether a use is allowed, ask the maintainers first.

## How to discuss with the maintainers

- Join our [discord server](https://discord.bfportal.gg/).
- Open a new issue.
- mail us at mail@bfportal.gg

# Development Environment Setup

## Containerized Setup

### Prerequisites

You need to install the following applications on your system

- [Python](https://www.python.org/downloads/) [^3.11]
- [Docker](https://www.docker.com)

## Todo
- [ ] docker `pre-commit` hooks in docker environment
  - all hooks except `commit-msg-validator` are working.

### Setup
- Clone in repo and cd into it
  ```
  git clone https://gh.bfportal.gg/
  ```
- Install [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management
  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Install project dependencies
  ```
  uv sync
  ```
- Install the pre-commit hooks by running
  ```
  uv run pre-commit install --install-hooks
  ```

- Copy the `.env.template` file to `.env`
- (optional) Create a [discord application](https://discord.com/developers/applications) for OAuth2 and copy the client id and secret
  - Paste the client id and secret in `.env` file to `DISCORD_CLIENT_ID` and `DISCORD_SECRET` respectively
- From the repositories root directory build the necessary docker images and run the platform
  ```
  docker-compose up
  ```
- The website should become available at `127.0.0.1:8000`

## Non-Container Environment Setup

### Prerequisites

You need to install the following applications on your system

- [Python](https://www.python.org/downloads/) [^3.11]
- [NodeJS / npm package manager](https://nodejs.org/en/download)
- [PostgreSQL](https://www.postgresql.org/)

### Setup

<!-- no need to create venv as poetry will create one -->


- Clone in repo and cd into it
  ```
  git clone https://gh.bfportal.gg/
  ```
- Install [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management
  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Install project dependencies
  ```
  uv sync
  ```
- Install the pre-commit hooks by running
  ```
  uv run pre-commit install --install-hooks
  ```
- Install npm dependencies
  ```
  cd bfportal.gg/bfportal
  npm install
  ```
- Copy the `.env.template` file to `.env`
- (optional) Create a [discord application](https://discord.com/developers/applications) for OAuth2 and copy the client id and secret

  - Paste the client id and secret in `.env` file to `DISCORD_CLIENT_ID` and `DISCORD_SECRET` respectively

- Make sure postgres is installed and running

  - Create DB, USER and Password for the project
  - Update the `.env` file accordingly

- Launch the server / web page with following commands(be sure to activate venv):

```
cd bfportal.gg/bfportal
python manage.py migrate --noinput
python manage.py ensure_superuser --username bfportal --email superuser@bfportal.com --password 1234
python manage.py ensure_initialization
python manage.py mock -u 3 -e 10 --clear
python manage.py runserver 0.0.0.0:8000
```
