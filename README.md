# Tracker
This project explores modular real-time computer control through the development of a target tracking camera gimbal. Emphasizing distributed processing and modular software design, it serves as an experimental platform for studying and advancing computer-controlled systems.
The electronics are developed in a [different project](http://github.com/leoole100/servo).

The architecture are multiple scripts that subscribe and publish streams using [ZeroMQ](http://zeromq.org/).

This was [implemented in python](software%20python/) for a 30 fps USB camera.

As this is not enough to reliably track movement of a fast moving ball through bounces a new (simpler) architecture in julia is [implemented](software%20julia/) to run at 120 fps on a CSI camera.

To install requierments on raspberry pi os:
```bash
sudo apt install python3-flask-socketio python3-picamera2 python3-opencv python3-serial
```

To autostart create a system service:
```bash
sudo nano /etc/systemd/system/tacker.service
sudo systemctl enable tracker.service 
```

```
[Unit]
Description=Tracker
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/leon/tracker/software/main.py

[Install]
WantedBy=multi-user.target
```