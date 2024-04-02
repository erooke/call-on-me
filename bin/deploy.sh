set -euxo pipefail

echo "Building..."
./bin/build-image.sh
echo "Pushing..."
./bin/push-image.sh
echo "Forcing the lambda to pick up the new image"
./bin/bump-lambda-image.sh
echo "Syncing..."
./bin/sync-bucket.sh