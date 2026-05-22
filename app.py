import os
import sys
import json
import pymysql
import boto3
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# --- CONFIGURATION (Fetch parameters safely from Environment Variables) ---
DB_HOST = os.environ.get("DB_HOST", "your-rds-endpoint.amazonaws.com")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "yourdbpassword")
DB_NAME = os.environ.get("DB_NAME", "inquirydb")

# AWS Service Configurations
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
SES_EMAIL_SENDER = os.environ.get("SES_EMAIL_SENDER", "your-verified-ses-email@gmail.com")
SES_EMAIL_RECEIVER = os.environ.get("SES_EMAIL_RECEIVER", "your-verified-ses-email@gmail.com")

# Initialize AWS Clients (Using IAM Instance Profile credentials automatically)
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
ses_client = boto3.client("ses", region_name=AWS_REGION)


# --- DATABASE INITIALIZATION FUNCTION ---
def init_db():
    """Initializes the MySQL database table if it doesn't already exist."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            # Create Database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
            cursor.execute(f"USE {DB_NAME};")
            
            # Create Inquiries Table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS inquiries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                customer_email VARCHAR(100) NOT NULL,
                message_text TEXT NOT NULL,
                ai_category VARCHAR(50) NOT NULL,
                urgency_score VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_query)
        connection.commit()
        connection.close()
        print("Database initialization executed successfully.", file=sys.stdout)
    except Exception as e:
        print(f"CRITICAL: Database initialization failed: {str(e)}", file=sys.stderr)


# --- AI TRIAGE LOGIC (AMAZON BEDROCK) ---
def triage_with_bedrock(message_content):
    """
    Invokes Amazon Bedrock using Anthropic Claude 3.5 Sonnet to strictly 
    categorize and score incoming text strings.
    """
    # System prompt design to ensure deterministic structural output
    prompt_data = (
        "You are an automated backend routing agent. Analyze the following customer message "
        "and classify it into exactly one of these categories: [Sales, Support, Billing, General]. "
        "Also, evaluate the objective business impact urgency score as exactly one of these: [Low, Medium, High].\n"
        "Output ONLY a raw JSON object containing exactly two keys: 'category' and 'urgency'. "
        "Do not include any introductory sentences, markdown blocks, formatting or conversational prose.\n\n"
        f"Customer Message: \"{message_content}\""
    )
    
    # Payload format structured for the updated Converse API / Messages API pattern
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt_data}]
            }
        ]
    }
    
    try:
        # Targeting the enterprise standard Claude 3.5 Sonnet model identifier
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(native_request)
        )
        
        response_body = json.loads(response.get('body').read())
        raw_text = response_body['content'][0]['text'].strip()
        
        # Clean up code blocks if model slips up structural enforcement rules
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
        parsed_result = json.loads(raw_text)
        return parsed_result.get("category", "General"), parsed_result.get("urgency", "Low")
        
    except Exception as e:
        print(f"ERROR: Bedrock invocation or parsing failed: {str(e)}", file=sys.stderr)
        # Fail-safe gracefully defaults rather than halting execution pipeline
        return "General", "Low"


# --- ROUTING ALERTS (AMAZON SES) ---
def send_priority_email(name, email, message, category, urgency):
    """Fires a high-priority structural tracking alert email to internal stakeholders via SES."""
    subject = f"🚨 URGENT {category.upper()} ACTION REQUIRED: Triage Alert"
    body_text = (
        f"An inquiry requiring high-priority attention has passed validation filters.\n\n"
        f"--- Pipeline Metadata ---\n"
        f"AI Category: {category}\n"
        f"Urgency Evaluation Score: {urgency}\n\n"
        f"--- Submission Details ---\n"
        f"Customer Identity: {name} ({email})\n"
        f"Original Message:\n{message}\n"
    )
    
    try:
        ses_client.send_email(
            Source=SES_EMAIL_SENDER,
            Destination={'ToAddresses': [SES_EMAIL_RECEIVER]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'}
                }
            }
        )
        print(f"Notification alert email dispatched via SES to {SES_EMAIL_RECEIVER}", file=sys.stdout)
    except Exception as e:
        print(f"ERROR: SES dispatch failure encountered: {str(e)}", file=sys.stderr)


# --- FLASK APPLICATION ROUTING VIEWS ---
@app.route("/", methods=["GET"])
def index():
    """Renders a simplified HTML web interface for contact submission form collection."""
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Customer Inquiry Intake Gateway</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; padding: 40px; margin: 0; }
            .card { max-width: 550px; background: white; margin: 0 auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
            h2 { color: #232f3e; margin-top: 0; border-bottom: 2px solid #eaeded; padding-bottom: 10px; }
            label { display: block; margin: 15px 0 5px; font-weight: bold; color: #4a5568; }
            input[type="text"], input[type="email"], textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e0; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
            textarea { height: 120px; resize: vertical; }
            button { background: #ff9900; color: white; border: none; padding: 12px 20px; font-size: 16px; font-weight: bold; border-radius: 4px; cursor: pointer; margin-top: 20px; width: 100%; transition: background 0.2s; }
            button:hover { background: #e68a00; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Submit Your Inquiry</h2>
            <form action="/submit" method="POST">
                <label for="name">Full Name</label>
                <input type="text" id="name" name="name" required placeholder="John Doe">
                
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" required placeholder="johndoe@example.com">
                
                <label for="message">Message</label>
                <textarea id="message" name="message" required placeholder="Describe your request or issue here..."></textarea>
                
                <button type="submit">Transmit Form Data</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)


@app.route("/submit", methods=["POST"])
def handle_submission():
    """Main execution route receiving raw payloads, driving AI assessment, and recording results."""
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")
    
    if not name or not email or not message:
        return "Bad Request: Missing payload fields.", 400

    # 1. Execute Intelligent AI Analysis Engine
    category, urgency = triage_with_bedrock(message)
    
    # 2. Persist State Log directly into the isolated RDS Cluster instance
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            insert_statement = """
            INSERT INTO inquiries (customer_name, customer_email, message_text, ai_category, urgency_score)
            VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_statement, (name, email, message, category, urgency))
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"DATABASE PERSISTENCE EXCEPTION: {str(e)}", file=sys.stderr)
        return "Internal Application Processing Failure.", 500

    # 3. Trigger Async Decoupled Alerts for High Urgency Escalations
    if urgency.lower() == "high" or category.lower() == "sales":
        send_priority_email(name, email, message, category, urgency)

    # 4. Success Dashboard Notice Template response representation
    success_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Submission Processed</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f6f9; padding: 40px; text-align: center; }}
            .box {{ max-width: 500px; background: white; margin: 50px auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 4px solid #4caf50; }}
            h3 {{ color: #2e7d32; }}
            p {{ font-size: 15px; color: #4b5563; }}
            .meta {{ background: #f9fafb; padding: 12px; margin: 15px 0; border-radius: 6px; border-left: 3px solid #ff9900; text-align: left; font-family: monospace; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h3>Submission Received Securely!</h3>
            <p>Your inquiry is currently being evaluated by our cloud operations engine routing queues.</p>
            <div class="meta">
                <strong>[Pipeline Classification]</strong><br>
                Assigned Domain: {category}<br>
                Impact Level: {urgency}
            </div>
            <a href="/">Submit another record</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(success_template)


# --- WORKER LAUNCH INVOCATION ---
if __name__ == "__main__":
    # Ensure tables exist dynamically before opening connection loops
    init_db()
    
    # Run server on port 80 or 8080. Binding to 0.0.0.0 exposes it to the internet via the EC2 Public IP.
    app.run(host="0.0.0.0", port=8080, debug=False)