#!/bin/bash

# Deploy script for Google Cloud Container Registry
# Usage: ./deploy.sh [tag]

set -e

# Default tag is latest if not provided
TAG=${1:-latest}
REPOSITORY="europe-west2-docker.pkg.dev/gen-lang-client-0386983970/event-finder/event-finder-app"

echo "Building Docker image with tag: $TAG for linux/amd64 platform"
docker buildx build --platform linux/amd64 -t $REPOSITORY:$TAG --push .

echo "Successfully deployed $REPOSITORY:$TAG"
echo "Image is now ready for Cloud Run deployment" 