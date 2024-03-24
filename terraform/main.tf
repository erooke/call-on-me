terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-2"
}

resource "aws_s3_bucket" "file-host" {
  bucket = "call-on-me-file-host"

  tags = {
    Name = "call-on-me-file-host"
  }
}

resource "aws_s3_bucket_ownership_controls" "file-host" {
  bucket = aws_s3_bucket.file-host.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "file-host" {
  bucket = aws_s3_bucket.file-host.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "file-host" {
  depends_on = [
    aws_s3_bucket_ownership_controls.file-host,
    aws_s3_bucket_public_access_block.file-host,
  ]

  bucket = aws_s3_bucket.file-host.id
  acl    = "public-read"
}

resource "aws_s3_bucket_website_configuration" "file-host" {
  bucket = aws_s3_bucket.file-host.id

  index_document {
    suffix = "index.html"
  }
}

resource "aws_cloudfront_distribution" "distribution" {
  enabled         = true
  is_ipv6_enabled = true

  origin {
    domain_name = aws_s3_bucket_website_configuration.file-host.website_endpoint
    origin_id   = aws_s3_bucket.file-host.bucket_regional_domain_name

    custom_origin_config {
      http_port                = 80
      https_port               = 443
      origin_keepalive_timeout = 5
      origin_protocol_policy   = "http-only"
      origin_read_timeout      = 30
      origin_ssl_protocols = [
        "TLSv1.2",
      ]
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
      locations        = []
    }
  }

  default_cache_behavior {
    cache_policy_id        = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = aws_s3_bucket.file-host.bucket_regional_domain_name
  }
}

resource "aws_iam_role" "function-role" {
  name = "function-role"
  path = "/"

  assume_role_policy = <<EOF
    {

  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

#Created Policy for IAM Role
resource "aws_iam_policy" "policy" {
  name        = "function-policy"
  description = "s3 all"


  policy = <<EOF
{
"Version": "2012-10-17",
"Statement": [
    {
        "Effect": "Allow",
        "Action": [
            "logs:*"
        ],
        "Resource": "arn:aws:logs:*:*:*"
    },
    {
        "Effect": "Allow",
        "Action": [
            "s3:*"
        ],
        "Resource": "arn:aws:s3:::*"
    }
]

}
    EOF
}

resource "aws_iam_role_policy_attachment" "test-attach" {
  role       = aws_iam_role.function-role.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_lambda_function" "call-on-me-updater-cron" {
  function_name = "call-on-me-updater-cron"
  timeout       = 15 # seconds
  memory_size   = 1024
  image_uri     = "698062986382.dkr.ecr.us-east-2.amazonaws.com/call-on-me:latest"
  package_type  = "Image"

  role = aws_iam_role.function-role.arn
}

resource "aws_cloudwatch_event_rule" "schedule" {
    name = "schedule"
    description = "Schedule for Lambda Function"
    schedule_expression = "rate(2 minutes)"
}

resource "aws_cloudwatch_event_target" "schedule_lambda" {
    rule = aws_cloudwatch_event_rule.schedule.name
    target_id = "processing_lambda"
    arn = aws_lambda_function.call-on-me-updater-cron.arn
}


resource "aws_lambda_permission" "allow_events_bridge_to_run_lambda" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.call-on-me-updater-cron.function_name
    principal = "events.amazonaws.com"
}