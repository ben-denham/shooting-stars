# Shooting Stars

Real-time web-app-controlled Christmas lights, built with Meteor and
Python.

## Development Environment

1. Make sure you have Docker and Docker Compose installed.
2. Create a `.env` file in this directory with the following format:
   ```
   ICICLES_TWINKLY_DEVICE_ID=<device-id>
   GRID_TWINKLY_DEVICE_ID=<device-id>
   CONE_TWINKLY_DEVICE_ID=<device-id>
   METEOR_TOKEN=<securely-generated-string>
   ```
3. Create a `web/meteor-settings.json` file in this directory with the following format:
   ```
   {
     "controllerToken": "<securely-generated-string>"
   }
   ```
4. Run:
   ```
   make deps
   make run
   ```

## Web Deployment

```
make run-bash service=web
meteor deploy <subdomain>.au.meteorapp.com --free --mongo --settings meteor-settings.json
```

## Controller Deployment

* On raspberry-pi, run `sudo apt install libatlas-base-dev` for
  numpy support.
* On raspberry-pi, install a rust compiler in order to build a wheel
  for River: https://linuxhint.com/install-rust-raspberry-pi/
* On raspberry-pi, install python3.11-dev for building a wheel for
  arc4
* Set up virtualenv inside `controller/`:
  * `python -m venv .venv`
  * `source .venv/bin/activate`
  * `python -m pip install -r requirements.txt`
* Place `controller/shooting-stars-lights.service` and  `controller/shooting-stars-blocks.service` in `/etc/systemd/system/`,
  updating the username and system paths, subdomain name, meteor token, and Twinkly device ID.
  * Note that any percentages in the token must be escaped by formatting them as double percentages.
* Start with `sudo systemctl restart shooting-stars-lights` and `sudo systemctl restart shooting-stars-blocks`
* Start at boot with `sudo systemctl enable shooting-stars-lights` and `sudo systemctl enable shooting-stars-blocks`
* View logs with `journalctl -fu shooting-stars-lights.service` and `journalctl -fu shooting-stars-blocks.service`
* Reload changes to service file with `sudo systemctl daemon-reload`
