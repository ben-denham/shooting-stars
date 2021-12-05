# Shooting Stars

Real-time web-app-controlled Christmas lights, built with Meteor and
Python.

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
