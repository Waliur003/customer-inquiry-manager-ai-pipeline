//VPC declaration with auto generation tag value to "InquiryManager"
resource "aws_vpc" "InquiryManager" {
    cidr_block = "10.0.0.0/16"
    tags = {
        Name = "InquiryManager"
    }

}


//Set Number of Availability Zones (AZs) to 2
data "aws_availability_zones" "available" {
  state = "available"
}

//Create 2 public subnets in the VPC
resource "aws_subnet" "public" {
    count = 2
    vpc_id = aws_vpc.InquiryManager.id
    cidr_block = "10.0.${count.index}.0/24"
    availability_zone = data.aws_availability_zones.available.names[count.index]
    tags = {
        Name = "Public Subnet ${count.index + 1}"
    }
}

//Create 2 private subnets in the VPC
resource "aws_subnet" "private" {
    count = 2
    vpc_id = aws_vpc.InquiryManager.id
    cidr_block = "10.0.${count.index + 10}.0/24"
    availability_zone = data.aws_availability_zones.available.names[count.index]
    tags = {
        Name = "Private Subnet ${count.index + 1}"
    }
}



//create internet gateway for the VPC
resource "aws_internet_gateway" "gw" {
    vpc_id = aws_vpc.InquiryManager.id
    tags = {
        Name = "InquiryManager-IGW"
    }
    }

//Create route table for public subnets
resource "aws_route_table" "public" {
    vpc_id = aws_vpc.InquiryManager.id
    tags = {
        Name = "Public Route Table"
    }
}

//Associate public subnets with the public route table
resource "aws_route_table_association" "public" {
    count = 2
    subnet_id = aws_subnet.public[count.index].id
    route_table_id = aws_route_table.public.id
}


//Create route to allow internet access from public subnets
resource "aws_route" "internet_access" {
    route_table_id = aws_route_table.public.id
    destination_cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
}





//create route table for private subnets
resource "aws_route_table" "private" {
    vpc_id = aws_vpc.InquiryManager.id
    tags = {
        Name = "Private Route Table"
    }
}

//Create VPC endpoint for S3 to allow private subnets to access S3 without going through the internet
resource "aws_vpc_endpoint" "s3" {
    vpc_id = aws_vpc.InquiryManager.id
    service_name = "com.amazonaws.${var.aws_region}.s3"
    route_table_ids = [aws_route_table.private.id]
    tags = {
        Name = "S3 VPC Endpoint"
    }
}



//Associate private subnets with the private route table
resource "aws_route_table_association" "private" {
    count = 2
    subnet_id = aws_subnet.private[count.index].id
    route_table_id = aws_route_table.private.id
}


