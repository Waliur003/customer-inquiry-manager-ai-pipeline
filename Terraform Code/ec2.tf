
//Data source to get the latest Amazon Linux 2 AMI ID for the EC2 instance
data "aws_ami" "amazon_linux" {
  most_recent = true
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["amazon"]
}



//Create EC2 instance named "Inquiry-App-Server" with Amazon Linux 2 AMI and connect it to the public subnet and security group "EC2-Web-SG" and conncet with IAM instance profile: Select project6role"
resource "aws_instance" "app_server" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro" //free tier eligible instance type
  subnet_id     = aws_subnet.public[0].id
  security_groups = [aws_security_group.EC2-Web-SG.name]
  iam_instance_profile = aws_iam_instance_profile.instance_profile.name
  tags = {
    Name = "Inquiry App Server"
  }
}

