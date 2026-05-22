//variable declarations for the project 



variable "aws_region" {
  description = "The AWS region in which to provision resources."
  type        = string
  default = "us-east-1"
}


variable db_username {
  description = "The username for the RDS database."
  type        = string
  
}


variable db_password {
  description = "The password for the RDS database."
  type        = string
}

