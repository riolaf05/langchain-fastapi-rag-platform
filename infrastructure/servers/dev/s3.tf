# module "iam-role" {
#   source = "git::https://github.com/riolaf05/terraform-modules//aws/s3?ref=v23.1.41"

#   project_info = {
#     name   = "news4p"
#     prefix = "news4p"
#     env    = "dev"
#   }

#   bucket_name      = "codedeploy-bucket"
#   ssm_param_prefix = "news4p"
#   user             = "arn:aws:iam::064856575681:user/rlaface"
# }

# locals {

# }

# data "aws_iam_policy_document" "s3_policy" {

#   statement {
#     actions   = ["s3:ListBucket"]
#     resources = ["arn:aws:s3:::news4p-codedeploy-bucket"]

#     principals {
#       type = "AWS"
#       identifiers = [
#         "arn:aws:iam::064856575681:user/rlaface"
#       ]
#     }
#   }

#   statement {
#     actions   = ["s3:Get*", "s3:List*", "s3:PutObject"]
#     resources = ["arn:aws:s3:::news4p-codedeploy-bucket", "arn:aws:s3:::news4p-codedeploy-bucket/*"]

#     principals {
#       type = "AWS"
#       identifiers = [
#         "arn:aws:iam::064856575681:user/rlaface"
#       ]
#     }
#   }
# }

# resource "aws_s3_bucket_policy" "s3_bucket_policy_stage" {
#   bucket = "news4p-codedeploy-bucket"
#   policy = data.aws_iam_policy_document.s3_policy.json
# }

module "s3-bucket-prod" {
  source = "git::https://github.com/riolaf05/terraform-modules//aws/s3?ref=v23.1.41"

  project_info = {
    name   = "news4p"
    prefix = "news4p"
    env    = "dev"
  }

  bucket_name      = "news4p-raw-documents-bucket"
  ssm_param_prefix = "news4p"
  user             = "arn:aws:iam::064856575681:user/rlaface"
}

# data "aws_iam_policy_document" "s3_policy_prod" {
#   statement {
#     actions   = ["s3:ListBucket"]
#     resources = ["${module.s3-bucket-prod.aws_s3_bucket.bucket.arn}"]

#     principals {
#       type = "AWS"
#       identifiers = [
#         "arn:aws:iam::064856575681:user/rlaface"
#       ]
#     }
#   }

#   statement {
#     actions   = ["s3:Get*", "s3:List*", "s3:PutObject"]
#     resources = ["${module.s3-bucket-prod.aws_s3_bucket.bucket.arn}", "${module.s3-bucket-prod.aws_s3_bucket.bucket.arn}/*"]

#     principals {
#       type = "AWS"
#       identifiers = [
#         "arn:aws:iam::064856575681:user/rlaface"
#       ]
#     }
#   }
# }

# resource "aws_s3_bucket_policy" "s3_bucket_policy_prod" {
#   bucket = module.s3-bucket-prod.aws_s3_bucket.bucket.id
#   policy = data.aws_iam_policy_document.s3_policy.json
# }

