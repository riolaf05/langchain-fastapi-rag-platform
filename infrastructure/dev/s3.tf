
module "s3" {
  source = "git::https://github.com/riolaf05/terraform-modules//aws/s3"

  project_info = {
    name   = "news4p"
    prefix = "news4p"
    env    = "dev"
  }

  bucket_name      = "raw-documents-bucket"
  ssm_param_prefix = "news4p"
  bucket_user_arn   = "arn:aws:iam::879338784410:user/rosario.laface"
}

resource "aws_s3_object" "object" {
  bucket = module.s3.bucket_name
  key    = "news4p/raw_documents/"
}
