# Contributing to bfportal.gg
> First off, thanks for taking the time to contribute! 🎉🎉

---

This file contains a few guidelines on how to contribute to the Battlefield Portal Library hosted at bfportal.gg
These are not rules but just some suggestion, so feel free to propose any change in the project

---

Before you start contributing you should understand the stack that this projects uses

![image](https://i.imgur.com/INghzbZ.png)

If you already have experience with django/wagtail, understanding the backend will be really easy for you. 
> **Note**
> If you are just starting it is highly recommended to learn about the structure of a [django project](https://docs.djangoproject.com/en/4.1/intro/tutorial01/). and [wagtail project](https://docs.wagtail.org/en/stable/getting_started/tutorial.html)

> Learn wagtail first :)

----
# Env Setup

Refer to [readme.md](/readme.md#how-to-run-locally)

----

The backend is made up of Four django Apps.

```
bfportal/
    bfportal (Global App)
    core (Content Server)
    factory (Fake data generation)
    theme (tailwind manager)
```
---
# Django Apps
|App|Description|
|----|----|
|bfportal|This app Contains the base settings and base html file that is used to generate any webpage on the website|
|core| The app is the heart of "Experience listing" and User profile, all the models used in the Database are defined in this|
|factory|Is an app that is used to generate fake data to help while developing the project locally|
|theme|This app is used to manage TailwindCSS integration with Django (start and upgrading)|

# Few key components
- All the "webpages" are in `<app>/<templates>/<app>/` directory, we can use this structure to override the template of other apps that are installed in python
- The models for all "pages" type are defined in [`/core/models/*`](/bfportal/core/models)
- The API at (https://api.bfportal.gg/) is defined and controlled by [`/core/api.py`](/bfportal/core/api.py)
- Form validation and discord hooks are done in [`/core/views.py`](/bfportal/core/views.py)

# How to contribute
- Pick an [issue](https://github.com/battlefield-portal-community/bfportal.gg/issues) or Create a new one explaning the change/feature you want to add
- Create a new branch for that issue
- Make your changes
- Make sure all the precommit test are passed
- Open a pull request to merge the branch into dev branch
- The changes will be reviewed on dev deployment
- Upon successfull testing dev will be merged into main

# How to discuss with the maintainers
- Join our [discord server](https://bfportal.gg/join).
- Open a new issue.
- mail us at mail@bfportal.gg
