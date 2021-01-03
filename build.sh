#!/bin/bash

Docker build -t cpn_generation ./source-code/
echo -e '\n\nSaving image...'
docker image save cpn_generation > cpn_generation.docker

read -n 1 -s -r -p $'\nScript complete. Press any key to continue.'