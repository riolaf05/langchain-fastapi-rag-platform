locals {
      PROJECT_NAME    = "rag-platform"
      ENV             = "dev"
      EC2_INSTANCE_IDs = "i-072579779a7ff289c" #dont use spaces
      REGION          = "eu-south-1"
}

module "turnon_ec2_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name          = "${local.PROJECT_NAME}-turnon-ec2-lambda"
  description            = "This function turn on the EC2 at a given time"
  handler                = "turnon_ec2.lambda_handler"
  runtime                = "python3.8"
  create_package         = false
  local_existing_package = "./src/turnon_ec2.zip"
  role_name              = "${local.PROJECT_NAME}-turnon-ec2-lambda-role"
  attach_policy          = true
  policy                 = aws_iam_policy.policy.arn
  environment_variables = {
    "EC2_INSTANCE_IDs"   = local.EC2_INSTANCE_IDs
    "LAMBDA_AWS_REGION" = local.REGION
  }

  tags = {
    PROJECT   = "POC"
    Terraform = true
  }
}

module "turnoff_ec2_lambda" {
source  = "terraform-aws-modules/lambda/aws"
version = "6.0.0"

function_name          = "${local.PROJECT_NAME}-turnoff-ec2-lambda"
description            = "This function turnoff the EC2 at a given time"
handler                = "turnoff_ec2.lambda_handler"
runtime                = "python3.8"
create_package         = false
local_existing_package = "./src/turnoff_ec2.zip"
role_name              = "${local.PROJECT_NAME}-turnoff-ec2-lambda-role"
attach_policy          = true
policy                 = aws_iam_policy.policy.arn
environment_variables = {
  "EC2_INSTANCE_IDs"   = local.EC2_INSTANCE_IDs
  "LAMBDA_AWS_REGION" = local.REGION
}

tags = {
    PROJECT   = "POC"
    Terraform = true
  }
}

resource "aws_iam_policy" "policy" {
  name        = "${local.PROJECT_NAME}-turn-on-off-ec2-lambda-policy"
  path        = "/"
  description = "Policy for turn on and off ec2 instances"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "TurnOnOffEC2",
        Action = [
          "ec2:Start*",
          "ec2:Stop*"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
    ]
  })
}