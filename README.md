# RoboFinal

## RoboMaster camera viewer

Connect the computer to the RoboMaster robot (the default configuration uses
the robot's Wi-Fi access-point mode), then install the dependencies and run:

```bash
python3 -m pip install -r requirements.txt
python3 src/camera_view.py
```

Press `q` or `Esc` in the camera window to stop. The connection type and video
resolution can also be selected explicitly:

```bash
python3 src/camera_view.py --connection ap --resolution 720p
```

Supported connection types are `ap`, `sta`, and `rndis`; supported resolutions
are `360p`, `540p`, and `720p`.

The viewer automatically looks for a solid red rectangular card. When it finds
one, it draws a green box around the card and shows `RED CARD DETECTED` in the
video window. If a small card is too far away to detect, lower the minimum pixel
area (lower values can also cause more false detections):

```bash
python3 src/camera_view.py --min-card-area 700
```
