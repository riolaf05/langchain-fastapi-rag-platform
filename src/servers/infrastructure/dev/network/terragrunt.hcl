locals {
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  #   environment_vars = "dev"
  #   # Extract out common variables for reuse
  #   env           = local.environment_vars.locals.environment
  project = local.environment_vars.locals.project_name
  profile = local.environment_vars.locals.profile
  region  = local.environment_vars.locals.region
}

include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "git::https://github.com/riolaf05/terraform-modules//aws/network"
}

inputs = {
  network-name        = "${local.project}"
  aws-profile         = "${local.profile}"
  region              = "${local.region}"
  availability-zones  = ["${local.region}a", "${local.region}c", "${local.region}d"]
  vpc-subnet-cidr     = "10.0.0.0/16"
  private-subnet-cidr = ["10.0.0.0/19", "10.0.32.0/19", "10.0.64.0/19"]
  db-subnet-cidr      = ["10.0.192.0/21", "10.0.200.0/21", "10.0.208.0/21"]
  enable_nat_gateway  = false
}


