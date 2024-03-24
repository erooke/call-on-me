set -euxo pipefail

FUNC_NAME=call-on-me-updater-cron
IMAGE_URI=$(aws lambda get-function --region us-east-2 --function-name $FUNC_NAME | jq -r '.Code.ImageUri')

aws lambda update-function-code --region us-east-2 --function-name $FUNC_NAME --image-uri "$IMAGE_URI"