# Victron HASS MQTT

Python application for transmitting VE.Direct data to an mqtt server via the Home Assistant MQTT specification to enable automatic device discovery

Hacked together based on code from: 
- https://github.com/leech001/hass-mqtt-discovery 
- https://github.com/karioja/vedirect

## Installation
Install via PIP:
```commandline
pip3 install git+https://github.com/metrafonic/victron-hass-mqtt
```
This should place an entrypoint for the code at `~/.local/bin/victron-mqtt`. 

Ensure that `~/.local/bin/` is added to your PATH or use the full path when running the code

## Usage:
```commandline
usage: victron-mqtt [-h] --tty TTY --name NAME [--timeout TIMEOUT] [--window_size WINDOW_SIZE] [--broker BROKER] [--port PORT]
                    [--username USERNAME] [--password PASSWORD] [--tls] [--ca_path CA_PATH]

Process VE.Direct protocol

optional arguments:
  -h, --help            show this help message and exit
  --tty TTY             Serial port
  --name NAME           MQTT Identifier
  --timeout TIMEOUT     Serial port read timeout
  --window_size WINDOW_SIZE
                        Sliding window moving average
  --broker BROKER       MQTT broker address
  --port PORT           MQTT broker port
  --username USERNAME   MQTT broker port
  --password PASSWORD   MQTT password
  --tls                 Use tls
  --ca_path CA_PATH     TLS CA cert path (required if using TLS)
```
NOTE: The windowing function defaults to 60, meaning that it will wait for 60 messages per variable, and average them out before sending.
This means that it will take up to 2 minutes for the first variables to appear in home-assistant.

## System service
Add the following to `/lib/systemd/system/victron.service`:
Remember to replace the arguments with your own variables
```text
[Unit]
Description=Victron MQTT
After=multi-user.target

[Service]
Type=simple
ExecStart=victron-mqtt --name Mobile-1 --tty /dev/ttyAMA0 --broker xxxxx --port 8883 --username mqtt --password xxxxxxxxxx --tls
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```
Reload and start the service:
```commandline
sudo systemctl daemon-reload
sudo systemctl enable victron
sudo systemctl start victron
```
