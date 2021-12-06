#!/bin/bash
pico2wave -l fr-FR -w test.wav "$1"
aplay -q test.wav
#rm test.wav

