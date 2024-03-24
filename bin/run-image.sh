set -euxo pipefail
source secrets.env

docker run \
    --rm \
    --platform linux/amd64 \
    -p 9000:8080 \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    adamhammes/call-on-me:latest