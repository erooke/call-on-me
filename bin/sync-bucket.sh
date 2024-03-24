set -euxo pipefail

echo Syncing html files...
aws s3 sync out/ s3://call-on-me-file-host --delete --acl public-read --exclude '*.*' --include '*.html' --cache-control 'no-cache, max-age=0'
echo Syncing assets...
aws s3 sync out/ s3://call-on-me-file-host --delete --acl public-read --include '*.*' --exclude '*.html' --cache-control 'public, max-age=315360000'
aws cloudfront create-invalidation --distribution-id=E2TVIJNYKH2WYK --paths='/*'