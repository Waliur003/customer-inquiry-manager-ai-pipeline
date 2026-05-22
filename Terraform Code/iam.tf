# 1. Define the Trust Policy allowing EC2 instances to assume this role
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# 2. Configure the actual IAM Role and link the trust policy
resource "aws_iam_role" "role" {
  name               = "project6-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# 3. Design the custom Least-Privilege Policy Document for Bedrock and SES
data "aws_iam_policy_document" "policy_doc" {
  statement {
    sid    = "BedrockServerlessInvocations"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel"
    ]
    resources = [
      "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
    ]
  }

  statement {
    sid    = "SESAsynchronousMailRouting"
    effect = "Allow"
    actions = [
      "ses:SendEmail"
    ]
    resources = ["*"] # SES authorization rules require wildcard or verified ARN scopes
  }
}

# 4. Create the managed IAM Policy using the corrected datasource name
resource "aws_iam_policy" "policy" {
  name        = "InquiryAppExecutionPolicy"
  description = "Provides runtime permissions for Bedrock AI triage and SES routing"
  policy      = data.aws_iam_policy_document.policy_doc.json
}

# 5. Attach the policy directly to the IAM role
resource "aws_iam_role_policy_attachment" "test-attach" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.policy.arn
}

# 6. The Missing Link: Create the IAM Instance Profile container for EC2
resource "aws_iam_instance_profile" "instance_profile" {
  name = "project6-instance-profile"
  role = aws_iam_role.role.name
}