module "sns" {
  source = "git::https://github.com/riolaf05/terraform-modules//aws/sns-bucket-notification"
  project_name = "news4p"
  bucket_name = module.s3.bucket_name
  bucket_arn = module.s3.bucket_arn
  filter_suffix = ".pdf"
  filter_prefix = aws_s3_object.object.key
}