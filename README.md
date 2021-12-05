# Shooting Stars

Real-time web-app-controlled Christmas lights, built with Meteor and
Python.

## Development Environment

Make sure you have Docker and Docker Compose installed, then run:

```
make deps
make run
```

## Web Deployment

```
make run-bash service=web
meteor deploy <subdomain>.au.meteorapp.com --free --mongo
```

## Controller Deployment

* Install dependencies with `python -m pip install -r
  controller/requirements.txt`
* On raspberry-pi, run `sudo apt-get install libatlas-base-dev` for
  numpy support.
* Place `controller/shooting-stars.service` in `/etc/systemd/system/`,
  updating the subdomain name.
* Start with `sudo systemctl restart shooting-stars`
* Start at boot with `sudo systemctl enable shooting-stars`
* View logs with `journalctl -fu shooting-stars.service`
* Reload changes to service file with `sudo systemctl daemon-reload`
