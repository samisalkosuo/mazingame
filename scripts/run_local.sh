#!/bin/bash

#run local docker image
echo "Run local image using:"
echo " "
echo "Without local volume:"
echo docker run -it --rm mazingame
echo " "
echo "With local volume:"
echo "docker run -it --rm -v <path_to_local_volume>:/mazingame/gamedata mazingame"

