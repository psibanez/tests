source /opt/aivero/rgbd_toolkit_armv8/aivero_environment.sh
export SERIAL=909512070859
gst-launch-1.0 realsensesrc serial=$SERIAL timestamp-mode=clock_all enable-color=true  ! rgbddemux name=demux demux.src_depth ! queue ! colorizer near-cut=300 far-cut=700 ! videoconvert ! glimagesink demux.src_color ! queue ! videoconvert ! glimagesink


