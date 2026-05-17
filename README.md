# Cloud Engineering Project 06: Customer Inquiry Manager (Intelligent AI Triage Pipeline)

## Overview

I architected and deployed a secure, two-tier intelligent web application on AWS. This project demonstrates the implementation of a robust infrastructure where customer inquiries are ingested via a persistent application tier, analyzed through generative artificial intelligence, and securely committed to an isolated relational database tier.

This architecture ensures:

- Strict data isolation
- Zero exposure of backend databases to the public internet
- Automated routing of high-priority business requests

---

# The Problem

Legacy customer service workflows and web intake architectures frequently suffer from two major issues:

- Operational bottlenecks
- Structural security risks

Manually sorting, tagging, and routing high volumes of customer emails or contact form submissions leads to:

- Delayed response times
- Lost sales opportunities
- Increased operational overhead

Additionally, simplistic architectures often place web hosting logic and transactional databases inside the same public-facing network, exposing sensitive customer records directly to the public internet and increasing the risk of exploitation.

---

# The Solution

## Stateful Web Hosting

Utilized Amazon EC2 to host a continuous, high-performance web application capable of managing persistent user sessions and incoming form requests.

## Intelligent AI Triage

Integrated Amazon Bedrock to dynamically evaluate ticket context and automatically classify customer inquiries into categories such as:

- Sales
- Support
- Billing

## Isolated Relational Storage

Deployed an Amazon RDS MySQL instance strictly inside private subnets, fully removing the persistence layer from direct public internet exposure.

## Automated Priority Routing

Configured Amazon SES to trigger immediate high-priority email notifications whenever urgent sales inquiries are identified by the AI classification layer.

---

# Tech Stack

| Category | Technology |
|---|---|
| Compute | Amazon EC2 (Amazon Linux 2023 / Python 3.12 / Flask) |
| Networking | Amazon VPC (Public & Private Subnets, Internet Gateway, Stateful Firewalls) |
| Database | Amazon RDS (MySQL Relational Database Service) |
| Artificial Intelligence | Amazon Bedrock (Anthropic Claude / Foundation Models) |
| Messaging | Amazon SES (Simple Email Service) |
| Security | IAM (Instance Profiles & Least-Privilege Policies) |

---

# Project Procedure

## 1. Engineered a Secure Network Topology

- Created a custom Amazon VPC named `InquiryManagerVPC`
- Provisioned two public subnets for external-facing web infrastructure
- Attached an Internet Gateway for inbound client traffic routing
- Provisioned two private subnets across separate Availability Zones
- Configured strict security groups:
  - `EC2-Web-SG` allowing inbound HTTP traffic
  - `RDS-DB-SG` allowing inbound MySQL traffic only from the EC2 security group on port `3306`

---

## 2. Deployed the Stateful Application Tier

- Launched an Amazon EC2 instance inside the public subnet using Amazon Linux 2023
- Deployed a Flask web application for:
  - Frontend rendering
  - Client request handling
  - POST payload ingestion
- Configured Python database drivers to support concurrent database communication

---

## 3. Integrated the Generative AI Brain

- Programmed the application runtime to securely send customer inquiries to Amazon Bedrock using the Boto3 SDK
- Designed deterministic prompt instructions for AI-driven triage classification
- Built validation logic to:
  - Parse AI response output
  - Assign standardized category labels
  - Generate urgency scoring based on business impact

---

## 4. Established the Relational Storage Tier

- Provisioned an Amazon RDS MySQL instance within a private DB subnet group
- Created normalized relational database schemas for:
  - Customer identity records
  - Inquiry content
  - AI classification metadata
  - Timestamp tracking
- Implemented structured SQL insert operations for every processed customer inquiry

---

## 5. Enforced Hardened Security (IAM)

- Configured a custom IAM Role attached directly to the EC2 instance using an IAM Instance Profile
- Applied least-privilege IAM policies granting:
  - `bedrock:InvokeModel`
  - `ses:SendEmail`
- Eliminated the need for hardcoded AWS credentials within the application environment

---

# Verification and Results

## Verified Successful Ingestion

Submitted live customer inquiries through the Flask interface and confirmed successful request parsing and connection handling.

## Validated AI Triage and Database Storage

Submitted a high-value quote inquiry and confirmed:

- Amazon Bedrock correctly classified the request as `"Sales"`
- Appropriate urgency flags were assigned
- Relational records were successfully inserted into the private MySQL database

## Confirmed Notification Delivery

Verified immediate receipt of Amazon SES notification emails whenever high-priority inquiries were processed.

---

# Architecture Diagram

_Add architecture diagram here._

---

# Verification Screenshots

## VPC Network Topology Configuration

Screenshot displaying:

- Public and private subnet segmentation
- Cross-Availability Zone routing tables
- Internet Gateway configuration

---

## Amazon Bedrock Model Access and Invocation Logs

Screenshot showing:

- Model access permissions
- Successful foundation model invocation responses

---

## EC2 Application Logs and Flask Server Output

Screenshot displaying:

- Inbound POST request parsing
- AI classification results
- Active database connection operations

---

## RDS MySQL Query Records

Screenshot confirming:

- Successful SQL query execution
- Stored customer inquiry records
- Labels and timestamp persistence

---

# Future Improvements

## Load Balancing and Auto Scaling

Implement:

- Application Load Balancer (ALB)
- Auto Scaling Group (ASG)

to improve scalability and high availability.

---

## Infrastructure as Code (IaC)

Refactor the complete infrastructure into Terraform configuration files for automated and repeatable deployments.

---

## Secrets Management

Migrate plaintext database credentials into AWS Secrets Manager to support:

- Secure secret retrieval
- Automated credential rotation

---

# Notes

This project reflects a production-oriented multi-tier AWS application architecture focused on:

- Strict network segmentation
- Relational database integrity
- Generative AI integration
- Secure administrative automation workflows
