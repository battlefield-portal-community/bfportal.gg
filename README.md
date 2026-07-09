<p align="center">
  <img width="300" src="https://raw.githubusercontent.com/battlefield-portal-community/Image-CDN/main/bf_portal_logo_bc.png#gh-dark-mode-only">
  <img width="300" src="https://raw.githubusercontent.com/battlefield-portal-community/Image-CDN/main/bf_portal_logo_noir.png#gh-light-mode-only">
  </p>

[![Docker Build](https://github.com/battlefield-portal-community/bfportal.gg/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/battlefield-portal-community/bfportal.gg/actions/workflows/main.yml)

# What is this ?

With the release of battlefield 2042, ripple effect studio, added the ability to make custom game modes called "experiences", currently there is no way to share a game mode outside of the game, this project aims to fill that gap.

# Info

Head over to [bfportal.gg](https://bfportal.gg/), and try it out

## Features

- User system (Discord login for integration with portal community discord server)
- Auto Fill API for forms
- Pagination and website wide search

## How it works

It is pretty straight forward

- You use your discord account to make a new account on the website and submit your experiences.
- On the submission page if u choose to share the playground Url of the experience, the submission form will autofill 😃.

You can later edit your experience if u like.

# How to Contribute

If you want to contribute to this project and the community, you're welcome to have a look at our [Contribution Guide](/CONTRIBUTING.md) for this project.

# Use of AI

We do **not** write the code for this project using AI. All code is written by hand by contributors. AI assistants (e.g. Claude Code) are used only for a small, well-defined set of tasks:

- **Talking through an approach** in plan mode — discussing structure, schema, and trade-offs. The contributor still writes all the code themselves (see [`CLAUDE.md`](/CLAUDE.md)).
- **The workflow automations defined in [`.claude/skills/`](/.claude/skills)** — currently `plan-issue` (turn an agreed plan into GitHub issues and cut a feature branch) and `open-pr` (open a PR and link the issues it closes).

Anything outside of the above is not an accepted use of AI in this repo. See the [Contribution Guide](/CONTRIBUTING.md#use-of-ai) for details.

# Special Thanks to

- [gametools.network](https://gametools.network/) for providing API to autofill submisson form 🥰
- [Wagtail](https://github.com/wagtail/wagtail) for providing an awesome framework that makes managing submissions very easy ✅
- [tailwindcss](https://github.com/tailwindlabs/tailwindcss) for saving the lives of backend developers. 🙏
- [Matavatar](https://discord.com/users/236802771381125120) from BFportal discord community for designing UI of the website 🤝
