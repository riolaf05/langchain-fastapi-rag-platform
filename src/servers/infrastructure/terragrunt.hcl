# ---------------------------------------------------------------------------------------------------------------------
# TERRAGRUNT CONFIGURATION
# Terragrunt is a thin wrapper for Terraform that provides extra tools for working with multiple Terraform modules,
# remote state, and locking: https://github.com/gruntwork-io/terragrunt
# ---------------------------------------------------------------------------------------------------------------------

#CANT USE UNTIL UPGRADE TO TERRAGRUNT > 0.54!!!
# locals {
#   # Automatically load environment-level variables
#   environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))

#   # Extract the variables we need for easy access
#   project =   local.environment_vars.locals.project
#   profile =   local.environment_vars.locals.profile
#   region  =   local.environment_vars.locals.region
#   state_bucket = local.environment_vars.locals.state_bucket

# }

locals {
  # Automatically load environment-level variables
  # environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))

  # Extract the variables we need for easy access
  project =   "news4p"
  profile =   "work_us"
  region  =   "us-east-1"
  state_bucket = "riassume-state-bucket"

}

# Generate an AWS provider block
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
    provider "aws" {
    region = "${local.region}"
    profile = "${local.profile}"
    default_tags {
        tags = {
        PROJECT       = "${local.project}"
        Terraform   = "true"
        }
      }
    }
    EOF
}

# Configure Terragrunt to automatically store tfstate files in an S3 bucket
remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket = "${local.state_bucket}"

    key     = "${local.project}/${path_relative_to_include()}/terraform.tfstate"
    region  = "${local.region}"
    profile = "work_us"
  }
}




# ---------------------------------------------------------------------------------------------------------------------
# GLOBAL PARAMETERS
# These variables apply to all configurations in this subfolder. These are automatically merged into the child
# `terragrunt.hcl` config via the include block.
# ---------------------------------------------------------------------------------------------------------------------

# Configure root level variables that all resources can inherit. This is especially helpful with multi-account configs
# where terraform_remote_state data sources are placed directly into the modules.
# inputs = merge(
#   # local.account_vars.locals,
#   # local.region_vars.locals,
#   local.environment_vars.locals,
# )
