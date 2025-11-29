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
   PRESENCE_TWINKLY_DEVICE_ID=<device-id>
   METEOR_TOKEN=<securely-generated-string>
   PRESENCE_METEOR_TOKEN=<securely-generated-string>
   ```
3. Create a `web/meteor-settings.json` file in this directory with the following format:
   ```
   {
     "blocksControllerTokens": [
       "secret_token_1"
     ],
     "presenceControllerTokensToConfig": {
       "secret_token_1": {
         "id": 1,
         "colour": "#FF0000"
       },
       "secret_token_2": {
         "id": 2,
         "colour": "#00FF00"
       },
       "secret_token_3": {
         "id": 3,
         "colour": "#0000FF"
       }
     }
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

1. Set up `web/meteor-settings.json` following this format:
   ```
   {
     "blocksControllerTokens": [
       "secret_token_1"
     ],
     "presenceControllerTokensToConfig": {
       "secret_token_1": {
         "id": 1,
         "colour": "#FF0000"
       },
       "secret_token_2": {
         "id": 2,
         "colour": "#00FF00"
       },
       "secret_token_3": {
         "id": 3,
         "colour": "#0000FF"
       }
     }
   }
   ```
2. Run:
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
* Place service files in `/etc/systemd/system/`, updating the username and system paths, Python venv path, subdomain name, meteor token, and Twinkly device ID:
  * `controller/shooting-stars-lights.service`
  * `controller/shooting-stars-blocks.service`
  * `controller/shooting-stars-cone.service`
  * `controller/shooting-stars-presence.service`
  * Note that any percentages in the token must be escaped by formatting them as double percentages.
* Start with:
  * `sudo systemctl restart shooting-stars-lights`
  * `sudo systemctl restart shooting-stars-blocks`
  * `sudo systemctl restart shooting-stars-cone`
  * `sudo systemctl restart shooting-stars-presence`
* Start at boot with:
  * `sudo systemctl enable shooting-stars-lights`
  * `sudo systemctl enable shooting-stars-blocks`
  * `sudo systemctl enable shooting-stars-cone`
  * `sudo systemctl enable shooting-stars-presence`
* View logs with:
  * `journalctl -fu shooting-stars-lights.service`
  * `journalctl -fu shooting-stars-blocks.service`
  * `journalctl -fu shooting-stars-cone.service`
  * `journalctl -fu shooting-stars-presence.service`
* Reload changes to service files with `sudo systemctl daemon-reload`

### Full Presence Setup

1. Install Raspberry Pi OS
   1. Pre-configure from Raspberry Pi Imager:
      1. Username and password
      2. Wi-Fi
      3. SSH Key
      4. Locale settings
2. Power on Raspberry Pi
3. Connect to your Raspberry Pi
   1. Make sure you're on the same 2Ghz network (ssh seems flakey otherwise)
   2. Find possible IPs with: `nmap -sP 192.168.1.0/24`
   3. Connect with: `ssh <ip-address>`
4. Basic Raspberry Pi configuration:
   1. Require password for sudo: `sudo mv /etc/sudoers.d/010_pi-nopasswd /etc/sudoers.d/.010_pi-nopasswd`
   2. `sudo apt update` and `sudo apt upgrade`
5. Enable shutdown via pins
   1. Add this line to `/boot/firmware/config.txt`:
      * `dtoverlay=gpio-shutdown,gpio_pin=21`
   2. Reboot
   3. Connect jumper leads to pins `39` (ground) and `40` (GPIO 20)
      * These are the two pins at the end closest to the USB ports
   4. Test safe shutdown:
      1. Touch two leads for 2 seconds
      2. Wait for green LED to stop blinking
      3. Disconnect power
6. Set up Presence
   1. `sudo apt install python3.11-dev libatlas-base-dev`
   2. `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
      * Select standard installation
      * Start a new SSH session to update `$PATH`
   3. `git clone https://github.com/ben-denham/shooting-stars.git`
   4. `cd shooting-stars/controller`
   5. `python3 -m venv .venv`
   6. `source .venv/bin/activate`
   7. `python -m pip install -r requirements.txt`
   8. Copy configured `shooting-stars-presence.service` to `/etc/systemd/system/`
   9. `sudo systemctl enable shooting-stars-presence`
   10. `sudo systemctl daemon-reload`
   11. `sudo systemctl restart shooting-stars-presence`

## Misc

* `assets/cone-layout-backup.json` can be restored with xled's `set_led_layout()`.
