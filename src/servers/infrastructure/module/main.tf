locals {
  # Automatically load environment-level variables
  # environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))

  # Extract the variables we need for easy access
  project      = "news4p"
  profile      = "work_us"
  region       = "us-east-1"
  state_bucket = "riassume-state-bucket"
  userdata     = <<-USERDATA
    #!/bin/bash
    cat <<"__EOF__" > /home/ec2-user/.ssh/config
    Host *
      StrictHostKeyChecking no
    __EOF__
    chmod 600 /home/ec2-user/.ssh/config
    chown ec2-user:ec2-user /home/ec2-user/.ssh/config
    sudo apt update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu  $(lsb_release -cs)  stable"
    sudo apt update
    sudo apt-get install -y docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo groupadd docker
    sudo usermod -aG docker ubuntu
    
  USERDATA

}

module "network" {

  source              = "git::https://github.com/riolaf05/terraform-modules//aws/network"
  network-name        = local.project
  region              = local.region
  availability-zones  = ["${local.region}a", "${local.region}c", "${local.region}d"]
  vpc-subnet-cidr     = "10.0.0.0/16"
  private-subnet-cidr = ["10.0.0.0/19", "10.0.32.0/19", "10.0.64.0/19"]
  db-subnet-cidr      = ["10.0.192.0/21", "10.0.200.0/21", "10.0.208.0/21"]
  enable_nat_gateway  = false
}


module "sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${local.project}-ec2-sg"
  description = "Security group for ${local.project} EC2 SG"
  vpc_id      = module.network.vpc-id

  ingress_with_cidr_blocks = [
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      description = "SSH"
      cidr_blocks = "0.0.0.0/0"
    },
    # {
    #   description              = "http from service one"
    #   rule                     = "http-80-tcp"
    #   source_security_group_id = aws_security_group.service_one.id
    # },
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      description = "All egress"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
}

module "asg" {
  source                    = "terraform-aws-modules/autoscaling/aws"
  name                      = "${local.project}"
  health_check_type         = "EC2"
  min_size                  = 0
  max_size                  = 1
  desired_capacity          = 1
  wait_for_capacity_timeout = "5m"
  user_data                 = base64encode(local.userdata)
  vpc_zone_identifier       = module.network.public-subnets
  instance_type             = "t2.small"
  image_id                  = "ami-07d9b9ddc6cd8dd30"
  security_groups           = [module.sg.security_group_id]
}

###CICD
# resource "aws_codedeploy_app" "codedeploy_app" {
#   name = "appexample-dev-codedeploy-us-east-1"
#   compute_platform = "Server"
# }

# resource "aws_codedeploy_deployment_group" "deployment_group" {
#   app_name              = aws_codedeploy_app.codedeploy_app.name
#   deployment_group_name = local.project
#   service_role_arn      = aws_iam_role.codedeploy_role.arn
#   deployment_config_name = "CodeDeployDefault.AllAtOnce"
#   autoscaling_groups = [module.asg.autoscaling_group.name]
#   auto_rollback_configuration {
#     enabled = false
#     events  = ["DEPLOYMENT_FAILURE"]
#   }
# }