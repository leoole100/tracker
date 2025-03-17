To install requirements on raspberry pi os:
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