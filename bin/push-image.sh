source secrets.env

set -euxo pipefail

docker tag adamhammes/call-on-me:latest 698062986382.dkr.ecr.us-east-2.amazonaws.com/call-on-me:latest
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 698062986382.dkr.ecr.us-east-2.amazonaws.com/
docker push 698062986382.dkr.ecr.us-east-2.amazonaws.com/call-on-me