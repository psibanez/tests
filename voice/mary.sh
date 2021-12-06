#!/bin/bash

# Version to adapt to your system
VERSION=5.2

#Check if our service is currently running
ps auxw | grep marytts-server | grep -v grep

# if the service is not running it returns a non zero to the environment viriable,
# in that case we start the service, else we ignore.
if [ $? != 0 ]
then
    #bash /local/mary/marytts/target/marytts-$VERSION/bin/marytts-server -Xmx2g
    sudo /opt/marytts-5.2/bin/marytts-server
fi

