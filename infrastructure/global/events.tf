module "turnoff_eventbridge" {
  source = "git::https://github.com/riolaf05/terraform-modules//aws/eventbridge"

  project_info = "${local.PROJECT_NAME}-turnoff-ec2-eventbridge"
  environment  = local.ENV
  # is_enabled      = true
  cron_expression = "cron(0 16 ? * MON-FRI *)" #in UTC
  lambda_arn      = module.turnoff_ec2_lambda.lambda_function_arn
  lambda_name     = module.turnoff_ec2_lambda.lambda_function_name
}

# module "turnon_eventbridge" {
#   source = "git::https://github.com/riolaf05/terraform-modules//aws/eventbridge"

#   project_info = "${local.PROJECT_NAME}-turnon-ec2-eventbridge"
#   environment  = local.ENV
#   # is_enabled      = true
#   cron_expression = "cron(0 8 ? * MON-FRI *)"  #in UTC
#   lambda_arn      = module.turnon_ec2_lambda.lambda_function_arn
#   lambda_name     = module.turnon_ec2_lambda.lambda_function_name
# }
