# Modular Tracking

Real-time object tracking is a core challenge in computer vision and
robotics. Moving a camera to track a ping pong ball during gameplay
creates an interesting platform to explore and evaluate detection,
tracking, and control strategies. This is due to its unique combination
of steady ballistic flight and rapid, complex bounces at high speeds.

To simplify the exploration of different strategies, the system is
designed with modularity and accessibility in mind. Each component is
built around high-level concepts, enabling users to experiment without
requiring an in-depth engineering background.

## Methods

The system is designed to track a ping pong ball in real time by moving
a camera dynamically. To achieve this, the project is broken down into
modular components, each addressing a specific aspect of the tracking
process.

The hardware components consists of a camera, motors, motor controllers
and a processing computer.\
For the camera a Raspberry Pi Camera V2 is used, as with the
[picamera2](https://github.com/raspberrypi/picamera2) software stack it
supports a framerate of 200 Hz.\
To move the camera 2 common stepper motors are mounted perpendicularly.
They are driven with field oriented controllers with the
[SimpleFOC](https://simplefoc.com/) firmware stack. They are connected
to the control computer using the Universal Serial Bus (USB).\
The chosen computer is a Raspberry Pi 5.

To power the components 9 V 3 A from a USB-C power supply are converted
to a 5 V 5 A bus for the computer and another 5 V 3 A bus for the
motors. Additionally the startup of the computer and the motors is
staggered. This was necessary to achieve stable operation.

To mount the components mechanically, they are designed as subrack
modules.

### Software

## Results

## Conclusion and Outlook
