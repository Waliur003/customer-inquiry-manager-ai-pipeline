//create aws_db_subnet_group for RDS instance named "inquiry-db-subnet-group" conneceted with the vpc "InquiryManager-vpc"
resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "inquiry-db-subnet-group"
    
  subnet_ids = aws_subnet.private[*].id
  tags = {
    Name = "DB Subnet Group"
  }
}

//Create RDS instance named "inquiry-db-instance" with MySQL engine and connect it to the db subnet group and security group "RDS-DB-SG"
resource "aws_db_instance" "inquiry-db-instance" {
  identifier              = "database-1"
  allocated_storage       = 20
  engine                  = "mysql"
  engine_version          = "8.0"
  instance_class          = "db.t2.micro"  //free tier eligible instance class
  db_name                 = "inquirydb"
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.db_subnet_group.name
  vpc_security_group_ids  = [aws_security_group.RDS-DB-SG.id]
  publicly_accessible     = false
  skip_final_snapshot     = true
  tags = {
    Name = "Inquiry DB Instance"
  }
}


