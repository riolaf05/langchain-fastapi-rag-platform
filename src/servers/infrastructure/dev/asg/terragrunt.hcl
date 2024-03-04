locals {
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  #   environment_vars = "${local.environment}"
  #   # Extract out common variables for reuse
  #   env           = local.environment_vars.locals.environment
  project     = local.environment_vars.locals.project_name
  environment = local.environment_vars.locals.environment
  profile     = local.environment_vars.locals.profile
  region      = local.environment_vars.locals.region
  userdata    = <<-USERDATA
    #!/bin/bash
    cat <<"__EOF__" > /home/ec2-user/.ssh/config
    Host *
      StrictHostKeyChecking no
    __EOF__
    chmod 600 /home/ec2-user/.ssh/config
    chown ec2-user:ec2-user /home/ec2-user/.ssh/config
    sudo apt update
    sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu  $(lsb_release -cs)  stable"
    sudo apt update
    sudo apt-get install docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo groupadd docker
    sudo usermod -aG docker ubuntu
  USERDATA
}

include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "tfr:///terraform-aws-modules/autoscaling/aws?version=7.4.0"
}

dependency "vpc" {
  config_path = "../network"
}

dependency "sg" {
  config_path = "../sg"
}

inputs = {

  name                      = "${local.project}-test"
  health_check_type         = "EC2"
  min_size                  = 0
  max_size                  = 1
  desired_capacity          = 1
  wait_for_capacity_timeout = "5m"
  user_data_base64          = base64encode(local.userdata)
  vpc_zone_identifier       = dependency.vpc.outputs.public-subnets
  instance_type             = "t2.small"
  image_id                  = "ami-07d9b9ddc6cd8dd30"
  security_groups           = [dependency.sg.outputs.security_group_id]

}

