provider "aws" {
  region  = "us-east-1"
  profile = "work_us"
  default_tags {
    tags = {
      PROJECT   = "NEWS4P"
      Terraform = "true"
    }
  }
}

