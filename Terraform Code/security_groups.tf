//Configure security groups for the EC2 instance webserver name "EC2-Web-SG"
resource "aws_security_group" "EC2-Web-SG" {
  name        = "EC2-Web-SG"
  description = "Security group for EC2 web server"
  vpc_id = aws_vpc.InquiryManager.id


//Allow inbound HTTP traffic on port 80 from any source
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }


//Allow inbound SSH traffic on port 22 from any source
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    }


// Allow Custom TCP traffic on port 8080 from any source
    ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    }

//Allow all outbound traffic from the EC2 instance
egress {
  from_port   = 0
  to_port     = 0
  protocol    = "-1" # Represents all protocols
  cidr_blocks = ["0.0.0.0/0"]
}

}


//Create security group again to Configure the Database Firewall for the RDS instance with name "RDS-DB-SG"
resource "aws_security_group" "RDS-DB-SG" {
  name        = "RDS-DB-SG"
  description = "Security group for RDS database"
  vpc_id      = aws_vpc.InquiryManager.id

  //Allow inbound MySQL traffic on port 3306 from the EC2-Web-SG security group
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.EC2-Web-SG.id]
  }


  //Allow all outbound traffic from the RDS instance
  egress {
  from_port   = 0
  to_port     = 0
  protocol    = "-1" # Represents all protocols
  cidr_blocks = ["0.0.0.0/0"]
}
}

