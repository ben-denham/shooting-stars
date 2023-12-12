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
5. NOTE: To test `deviceorientation` events for the `cone`, the
   website needs to be served over https (e.g. with a simple proxy).

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
* Place service files in `/etc/systemd/system/`, updating the username and system paths, subdomain name, meteor token, and Twinkly device ID:
  * `controller/shooting-stars-lights.service`
  * `controller/shooting-stars-blocks.service`
  * `controller/shooting-stars-cone.service`
  * Note that any percentages in the token must be escaped by formatting them as double percentages.
* Start with:
  * `sudo systemctl restart shooting-stars-lights`
  * `sudo systemctl restart shooting-stars-blocks`
  * `sudo systemctl restart shooting-stars-cone`
* Start at boot with:
  * `sudo systemctl enable shooting-stars-lights`
  * `sudo systemctl enable shooting-stars-blocks`
  * `sudo systemctl enable shooting-stars-cone`
* View logs with:
  * `journalctl -fu shooting-stars-lights.service`
  * `journalctl -fu shooting-stars-blocks.service`
  * `journalctl -fu shooting-stars-cone.service`
* Reload changes to service files with `sudo systemctl daemon-reload`

## Misc

* `assets/cone-layout-backup.json` can be restored with xled's `set_led_layout()`.
