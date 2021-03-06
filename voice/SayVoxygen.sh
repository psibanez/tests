#!/bin/bash
####################################################
# Trim leading and trailing whitespace from string #
####################################################
trim() {
    # Determine if 'extglob' is currently on.
    local extglobWasOff=1
    shopt extglob >/dev/null && extglobWasOff=0 
    (( extglobWasOff )) && shopt -s extglob # Turn 'extglob' on, if currently turned off.
    # Trim leading and trailing whitespace
    local var=$1
    var=${var##+([[:space:]])}
    var=${var%%+([[:space:]])}
    (( extglobWasOff )) && shopt -u extglob # If 'extglob' was off before, turn it back off.
    echo -n "$var"  # Output trimmed string.
}

#########################################################
# Script usage : ./SayVoxygen.sh [Voice] [Text To Say]  #
# Ex: ./SayVoxygen.sh Electra "Bonjour"		            #
# See https://www.voxygen.fr/ demo for available voices #
#########################################################
#1st HTTP GET request to obtain mp3 URL in header
VOXY_URL="https://www.voxygen.fr/sites/all/modules/voxygen_voices/assets/proxy/index.php"
HEADER=$(curl -sS -G -X HEAD -i $VOXY_URL --data-urlencode "method=redirect" --data-urlencode "text=$2" --data-urlencode "voice=$1")
IFS=$'\n'; arrHEAD=($HEADER); unset IFS;
for i in "${arrHEAD[@]}"
do
        IFS=$':' ; arrLine=($i); unset IFS;
        S=$(trim "${arrLine[0]}")
        if [ "$S" = "Location" ]; then
                MP3_URL="https:"$(trim "${arrLine[1]}")
                #2nd HTTP GET request to download mp3 file
                curl -sS $MP3_URL > /tmp/tts.mp3
                #Playing mp3 file
                mpg123 -q /tmp/tts.mp3
                break	
    	fi
done
