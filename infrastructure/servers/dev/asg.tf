# locals {
#   # environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
#   environment_vars = "dev"
#   # Extract out common variables for reuse
#   env           = local.environment_vars.locals.environment
#   # project       = local.environment_vars.locals.project
#   # cluster_name  = local.environment_vars.locals.cluster_name
#   # aws_region    = local.region_vars.locals.aws_region
# }

module "ec2-asg" {

  source = "git::https://github.com/riolaf05/terraform-modules//aws/autoscaling-elb?ref=v23.1.57"
  project_info = {
    name   = "news4p-asg"
    prefix = "news4p-asg"
    env    = "dev"
  }

  aws_provider_info = {
    region  = "eu-west-1"
    profile = "news4p"
  }


  /* EC2*/
  instance_type = "t3.micro"
  user_data     = <<EOT
#!/bin/bash
cd ~ 
sudo yum install -y ruby 
wget https://aws-codedeploy-ap-northeast-1.s3.ap-northeast-1.amazonaws.com/latest/install
chmod +x ./install 
sudo ./install auto 
sudo service codedeploy-agent start 
sudo service codedeploy-agent status
   EOT

  vpc-id     = module.network.vpc_id
  public     = false
  ami        = "ami-0bba69335379e17f8"
  public_key = ""
}
