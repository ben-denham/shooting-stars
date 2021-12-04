# Shooting Stars

Meteor.js + Python project

## Development Environment

Make sure you have Docker and Docker Compose installed, then run:

```
make deps
make run
```

## Deployment

```
make run-bash service=web
meteor deploy <subdomain>.au.meteorapp.com --free --mongo
```
