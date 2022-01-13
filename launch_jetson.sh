CAMERA='/dev/video0'
MODEL_LOCATION='graphs/InceptionV4_TensorFlow/graph_inceptionv4_tensorflow.pb'
INPUT_LAYER='input'
OUTPUT_LAYER='InceptionV4/Logits/Predictions'
GST_DEBUG=inceptionv4:6 gst-launch-1.0 \
v4l2src device=$CAMERA ! videoconvert ! videoscale ! queue ! net.sink_model \
inceptionv4 name=net model-location=$MODEL_LOCATION backend=tensorflow backend::input-layer=$INPUT_LAYER  backend::output-layer=$OUTPUT_LAYER
