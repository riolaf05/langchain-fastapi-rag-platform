# resource "aws_iam_instance_profile" "ec2_profile_hello_world" {
#   name = "ec2_profile_hello_world"
#   role = aws_iam_role.ec2_role_hello_world.name
# }

# resource "aws_iam_role_policy" "ec2_policy" {
#   name = "ec2_policy"
#   role = aws_iam_role.ec2_role_hello_world.id

#   policy = <<EOF
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Action": [
#         "ecr:GetAuthorizationToken",
#         "ecr:BatchGetImage",
#         "ecr:GetDownloadUrlForLayer"
#       ],
#       "Effect": "Allow",
#       "Resource": "*"
#     }
#   ]
# }
# EOF
# }