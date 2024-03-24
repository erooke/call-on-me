set -euxo pipefail

docker build --platform linux/amd64 -t adamhammes/call-on-me:latest .