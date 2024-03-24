set -euxo pipefail

echo "Building..."
./bin/build-image.sh
echo "Pushing..."
./bin/push-image.sh
echo "Forcing the lambda to pick up the new image"
./bin/bump-lambda-image.sh
echo "Invoking the lambda"
./bin/invoke-lambda.sh
echo "Invalidating the Cloudfront cache"
./bin/invalidate-cloudfront.sh