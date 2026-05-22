# Cloud Engineering Project 06: Customer Inquiry Manager (Intelligent AI Triage Pipeline)

## Overview

I have architected and deployed a highly secure, enterprise-grade multi-tier intelligent application on AWS. This project demonstrates production-ready cloud practices by isolating database transactions within secure, private network boundaries, leveraging persistent compute primitives, and integrating generative artificial intelligence via serverless APIs. The pipeline ingests unstructured public web forms, processes them through an LLM orchestration layer to extract structured metadata, writes transactional logs to a private relational backend, and routes asynchronous notifications based on intent—all without exposing sensitive storage vectors to the public internet.

---

## The Problem

Modern web infrastructure and client intake portals are frequent targets for corporate exploitation and bottleneck inefficiencies. Legacy configurations consistently suffer from two foundational architectural flaws:

### Network Exposure Risks
Placing presentation frontends and transactional database components inside shared, public-facing subnets increases the vector area for cross-site scripting, SQL injections, and unauthorized internet scans.

### Operational Intakes Bottlenecks
Manual triage of customer complaints, technical bugs, billing conflicts, and high-value sales requests creates severe administrative lag. This fragmentation drops critical business revenue opportunities and stretches response metrics beyond optimal limits.

---

## The Solution

### Stateful Production Hosting Tier
Leveraged a dedicated Amazon EC2 compute footprint configured with web frameworks to handle steady-state incoming client request streams, process continuous connection handshakes, and isolate backend operational scripts.

### Decoupled Generative AI Orchestration
Integrated Amazon Bedrock running the enterprise-tier Anthropic Claude 3.5 Sonnet foundation model. The system processes raw, unstructured strings into strict JSON objects containing classified business domains and calculated urgency weights on the fly.

### Hardened Relational Data Isolation
Provisioned an Amazon RDS MySQL instance strictly inside an isolated multi-AZ private subnet array. Database access is entirely unreachable from the public internet, satisfying stringent compliance and data-at-rest isolation patterns.

### Automated Contextual Mail Routing
Programmed Amazon SES to act as an asynchronous notification engine. The application intercepts priority markers evaluated by the artificial intelligence layer and instantly fires escalated triage briefs to targeted corporate mail streams.

---

## Tech Stack

**Compute:** Amazon EC2 (Amazon Linux 2023 / Python 3.12 / Flask / PyMySQL)

**Networking:** Amazon VPC (Public & Private Subnets, Internet Gateway, Stateful Firewalls, DB Subnet Groups)

**Database:** Amazon RDS (MySQL Engine Version 8.0+)

**Artificial Intelligence:** Amazon Bedrock (Anthropic Claude 3.5 Sonnet Serverless Model Invocations)

**Messaging:** Amazon SES (Simple Email Service Sandbox API Engines)

**Security & Governance:** IAM (Instance Profiles, Scoped Assumed Roles, Least-Privilege Trust Policies)

---

## Architecture Diagram

---

## Project Procedure

### 1. Network Topology Engineering & Security Contouring

I engineered a highly segmented custom network block using Amazon VPC (InquiryManagerVPC) allocating a /16 CIDR range to achieve complete architectural isolation.

#### Subnet Partitioning
Provisioned two Public Subnets across alternate Availability Zones mapped to an Internet Gateway for external ingress. Concurrently, provisioned two Private Subnets completely devoid of public routing tables to house the persistence layer.

#### Stateful Security Group Matrix
Designed a strict multi-tier firewall hierarchy. The web server firewall (EC2-Web-SG) explicitly constrains public access to inbound TCP port 8080 (Flask application listener) and port 22 (scoped to administrator IP addresses). The database firewall (RDS-DB-SG) restricts inbound connections to TCP port 3306, dynamically matching traffic only if the packet source originates from the explicit security group identifier of the EC2 instance profile.

---

### 2. Application Tier Deployment & Client-Side Ingestion

I deployed an active compute instance within the public network space running the optimized Amazon Linux 2023 runtime.

#### Web Ingestion Application
Built and initialized a native Flask service handling concurrent client interaction parameters. The server hosts an input portal parsing multi-part text form data payloads.

#### Database Integration Architecture
Configured the application scope with native, low-latency client drivers (PyMySQL) wrapped in structural context handlers to systematically establish execution loops over the internal private VPC network path.

---

### 3. Generative AI Logic Integration (Amazon Bedrock)

I configured the application engine to communicate securely with serverless models on Amazon Bedrock, eliminating the need for self-hosted machine learning clusters.

#### Deterministic Prompt Engineering
Implemented strict system conditioning constraints using the Boto3 SDK, forcing Anthropic Claude 3.5 Sonnet to evaluate input texts objectively. The model skips conversational prose or markdown formatting and natively returns a raw, pre-formatted JSON string.

#### Triage Extraction Schema
The metadata parsing layer evaluates customer intent against explicit definitions, mapping data states dynamically into designated keys (category -> Sales, Support, Billing, General | urgency -> Low, Medium, High).

---

### 4. Relational Storage Architecture (Amazon RDS)

I provisioned a managed Amazon RDS MySQL instance attached directly to a custom private DB Subnet Group across isolated Availability Zones.

#### Database Schema Creation
Wrote relational SQL initialization scripts executing dynamically on startup to confirm physical table consistency. The storage map utilizes data column structures designed to handle data tracing metrics:

```sql
CREATE TABLE IF NOT EXISTS inquiries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(100) NOT NULL,
    message_text TEXT NOT NULL,
    ai_category VARCHAR(50) NOT NULL,
    urgency_score VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Transactional Ledger Processing
Every submitted payload uses sanitized, parameterized query runs to commit text payloads, timestamp records, and AI classification calculations directly to the hidden relational cluster.

---

### 5. IAM Policy Enforcement & Least-Privilege Hardening

To prevent security vulnerability vectors, I built a zero-trust credential model avoiding hardcoded secrets or static API access keys inside code.

#### IAM Instance Profile
Created an execution role attached natively to the EC2 server instance.

#### Scoped Policy Parameters
Built custom JSON configuration statements restricting resource capabilities strictly to the operations required for the system pipeline to run:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockModelInvocation",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
        },
        {
            "Sid": "SESSendingPermissions",
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## Infrastructure as Code (IaC) Architecture

To enforce the core cloud engineering principles of repeatability, drift detection, and immutable infrastructure, the entire multi-tier environment is provisioned using declarative **Terraform (v1.0+)** configurations. The codebase is strictly decoupled into modular component files to segregate logic domains (Network, Compute, Storage, and Identity) and to allow scalable infrastructure management.

###  Directory Layout & Modular Structure

The workspace is organized using a flat, high-readability layout optimized for granular component modifications:

```text
customer-inquiry-manager-ai-pipeline/
├── provider.tf          # Core initialization and cloud provider scoping
├── variables.tf         # Parameter types, validations, and default definitions
├── terraform.tfvars     # Environment-specific configuration parameter values
├── vpc.tf               # Isolated network primitives (VPC, Subnets, Gateways, Routes)
├── security_groups.tf   # Stateful firewall boundaries and port configurations
├── iam.tf               # Role definitions, assume trusts, and instance profiles
└── ec2.tf               # Stateful web server configurations and AMI data lookups
```

---

##  Detailed File-by-File Technical Breakdown

### 1. Provider Configurations (`provider.tf`)

**Provider Scoping:** Declares the minimum required provider version constraint (`hashicorp/aws ~> 4.0`) to avoid execution breaking changes across major versions.

**Regional Binding:** Targets the dynamic region variable (`var.aws_region`) to safely establish consistent resource provisioning constraints.



### 2. Isolated Network Topology (`vpc.tf`)

**VPC Partitioning:** Provisions a hard-bordered custom network block (`aws_vpc.InquiryManager`) allocating a `/16` CIDR block for deep architectural isolation.

**Availability Zone Distribution:** Utilizes the dynamic `aws_availability_zones` data source to distribute an array of 2 Public Subnets and 2 Private Subnets cleanly across alternate physical availability zones using `count` and indexing loops.

**Routing and Egress Gateways:** Attaches an `aws_internet_gateway` to handle all public inbound client handshakes. Concurrently maps an internal `aws_vpc_endpoint` (Gateway Endpoint) for Amazon S3 to the private route table, allowing the database layer to communicate with internal AWS systems entirely over the isolated AWS private backbone network.



### 3. Stateful Security Infrastructure (`security_groups.tf`)

#### Tier 1 Presentation Firewall (`EC2-Web-SG`)

Implements strict public ingress bounds on TCP Port 8080 (Flask application worker endpoint) and TCP Port 22 (secured administrator gateway connect path). Includes an unrestricted egress block (`protocol = "-1"`) to allow the server to transmit outbound runtime API requests out to Amazon Bedrock and SES.

#### Tier 2 Storage Firewall (`RDS-DB-SG`)

Constructs a zero-trust network perimeter around the persistence tier. It blocks all broad public internet traffic entirely, explicitly restricting inbound execution parameters on TCP Port 3306 (MySQL) to traffic originating exclusively from the security group identifier of the web server.



### 4. Managed Relational Database Storage (`rds.tf`)

**Subnet Group Boundaries:** Configures an `aws_db_subnet_group` passing an active array containing only the private subnets, ensuring physical cluster hardware is never provisioned within a public network block.

**Database Customization Parameters:** Launches an `aws_db_instance` running the optimized MySQL 8.0 engine on free-tier compliant infrastructure. The instance enforces security best practices by explicitly hardcoding `publicly_accessible = false` and `skip_final_snapshot = true` to allow smooth sandbox environment lifecycles.



### 5. Least-Privilege Identity & Access Governance (`iam.tf`)

**Assume Role Trusts:** Builds an execution trust structure via an `aws_iam_policy_document` data source that securely allows the Amazon EC2 service to assume identity properties dynamically at runtime.

**Granular Policy Design:** Implements structural least-privilege permissions, completely avoiding broad wildcard access. The policy explicitly constrains actions down to a single foundation model ARN for AI queries and locks down messaging actions strictly to necessary mail primitives:

```hcl
# Scoped permissions mapped within iam.tf
actions   = ["bedrock:InvokeModel"]
resources = ["arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"]
```

**The Instance Profile Container:** Explicitly wraps the generated role inside an `aws_iam_instance_profile` block, establishing the logical interface required to bridge IAM policies directly over to live compute instance hardware frames.



### 6. Compute Instance Provisioning (`ec2.tf`)

**Dynamic OS Lookups:** Deploys an `aws_ami` data engine block to automatically evaluate and select the most recent, performance-tuned Amazon Linux HVM image ID metadata string on startup.

**Role Identity Attachment:** Sets the `iam_instance_profile` reference parameter directly to the instance profile container defined inside the identity file. This enables the Flask code running inside the server to perform secure, credential-free AWS API calls without hardcoding static keys.



##  Security & Parameters Architecture (`variables.tf` & `terraform.tfvars`)

**Credential Decoupling:** Database structural parameters such as `db_username` and `db_password` are declared as strongly typed variables without fallback values inside `variables.tf`.

**The Guardrail Rule:** Local execution credentials are assigned values exclusively within `terraform.tfvars`. This local parameters configuration is explicitly targeted inside the `.gitignore` asset log to prevent sensitive production strings from leaking into public Git version control streams.

---

## Verification and Results

### Verified Successful Ingestion

Submitted test payloads directly to the live server at http://18.234.97.238:8080. Application terminal logs verified smooth frame handshakes, real-time context captures, and zero dropping of client transport data strings.

### Validated AI Triage and Private Relational Storage

Injected testing data simulating high-value sales requests (e.g., pricing options for large enterprise teams). The Amazon Bedrock integration interpreted the intent, outputted a clean JSON classification string, and successfully executed a secure network transaction to record the new entry within the database.

---

## Verification Screenshots

### VPC Network Topology Configuration
Screenshot of the VPC dashboard displaying public and private subnet partitions alongside cross-AZ routing tables confirming hard network boundaries.
<img width="1919" height="911" alt="Screenshot 1" src="https://github.com/user-attachments/assets/0d777494-5b60-4b35-91c2-f9b6d74023c9" />


### EC2 Application Logs and Flask Server Output
Screenshot of the live application console showing inbound POST data parsing, successful Bedrock model invocation responses, and active database query loops.
<img width="1908" height="540" alt="Screenshot 2" src="https://github.com/user-attachments/assets/96b8bc40-a2e7-40ef-a183-7743fcd75ff6" />


### RDS MySQL Query Records
Screenshot showing standard SQL selection results (`SELECT * FROM inquiries;`) executed directly inside the private database instance, confirming successful storage of queries, categories, and priority flags.
<img width="1904" height="534" alt="Screenshot 3" src="https://github.com/user-attachments/assets/ce9c0c99-10ec-4fde-bfba-a6d7e3f6d894" />


### Frontend Client Request Portal Ingestion
Screenshot of the custom Flask frontend interface showcasing data capture fields, server context handling, and user transmission triggers.
<img width="1760" height="778" alt="Screenshot 4" src="https://github.com/user-attachments/assets/b313bd86-1ea2-4c33-bf35-c1ca66f39efb" />


### Live Application Pipeline Metric Response
Screenshot of the dynamic output template verifying successful connection validation rules, real-time classification parsing, and transaction tracking updates.
<img width="1919" height="623" alt="Screenshot 5" src="https://github.com/user-attachments/assets/b361fa8b-fcf3-42b0-8715-0734a3649577" />

---

## Future Improvements

### High Availability and Scalability Implementation
Introduce an Elastic Load Balancer (ELB) alongside an Auto Scaling Group (ASG) across the public subnets to automatically scale the compute layer based on web traffic.

### Enterprise Secrets Governance
Migrate raw database login credentials out of server variables and store them inside AWS Secrets Manager, configuring programmatic lookups and automated password rotations to enforce stricter data compliance profiles.

---

## Notes

This architecture demonstrates a secure, multi-tier deployment pattern. It highlights key skills in managing isolated network paths, relational state rules, enterprise application compute, serverless generative AI APIs, and decoupled asynchronous messaging frameworks.
