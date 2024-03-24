set -euxo pipefail

DISTRIBUTION_ID=E2TVIJNYKH2WYK
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"