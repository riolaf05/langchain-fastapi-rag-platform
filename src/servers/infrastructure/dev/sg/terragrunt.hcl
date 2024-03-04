locals {
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  #   environment_vars = "${local.environment}"
  #   # Extract out common variables for reuse
  #   env           = local.environment_vars.locals.environment
  project     = local.environment_vars.locals.project_name
  environment = local.environment_vars.locals.environment
  profile     = local.environment_vars.locals.profile
  region      = local.environment_vars.locals.region

}

terraform {
  source = "tfr:///terraform-aws-modules/security-group/aws?version=5.1.1"
}

dependency "vpc" {
  config_path = "../network"
}

inputs = {
  name        = "${local.project}-ec2-sg"
  description = "Security group for ${local.project} EC2 SG"
  vpc_id      = dependency.vpc.outputs.vpc-id

  ingress_with_cidr_blocks = [
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      description = "SSH"
      cidr_blocks = "0.0.0.0"
    },
    # {
    #   rule        = "postgresql-tcp"
    #   cidr_blocks = "0.0.0.0/0"
    # },
  ]
}