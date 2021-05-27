#! /bin/bash

echo "[WARN] The built pica_dev image is large (around 1GB). Are you sure to build the image? ([y]/n)"

echo "Build docker images for pica_dev object detection..."
# --squash: Squash newly built layers into a single new layer
# Used to reduce built image size.
sudo docker build -t pica_dev:4 -f ./Dockerfile.pica_dev .
sudo docker image prune --force

