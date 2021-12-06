#!/bin/sh
# Show a webcam that delivers video 1920x1080 MJPG on screen
VELEM="v4l2src device=/dev/video0"
VCAPS="image/jpeg, width=600, height=400, framerate=30/1"
VSOURCE="$VELEM ! $VCAPS"
VIDEO_SINK="videoconvert ! videoscale ! xvimagesink sync=false"
VIDEO_DECODE="jpegparse ! jpegdec"

# echo is just for debugging purposes
echo gst-launch-1.0 -vvv \
	$VSOURCE \
   	! $VIDEO_DECODE \
   	! $VIDEO_SINK 

gst-launch-1.0 -vvv \
	$VSOURCE \
   	! $VIDEO_DECODE \
   	! $VIDEO_SINK 
    