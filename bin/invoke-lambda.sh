source secrets.env

set -euxo pipefail

aws lambda invoke \
  --function-name=call-on-me-updater-cron \
  --region us-east-2 \
  /dev/stdout