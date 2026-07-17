import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import logging
import re

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# SMTP Configuration
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'projectmail2425@gmail.com'
SMTP_PASSWORD = 'yrgb qyqz twkw pbdp'
SMTP_FROM_EMAIL = 'projectmail2425@gmail.com'

def send_smtp_email(to_email, subject, html_body, plain_text_body=None):
    """
    Send email using SMTP with HTML content
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        if plain_text_body:
            part1 = MIMEText(plain_text_body, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def generate_order_confirmation_email(data):
    """
    Generate HTML email content for order confirmation
    """
    customer_name = data.get('customer_name', 'Customer')
    order_id = data.get('order_id', 'N/A')
    product_names = data.get('products', '')
    total_amount = data.get('total_amount', '0.00')
    email = data.get('email', '')
    phone = data.get('phone', '')
    address = data.get('address', '')
    order_date = datetime.now().strftime('%B %d, %Y %I:%M %p')

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 10px 10px 0 0;
                margin: -30px -30px 20px -30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .order-details {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
            }}
            .status-badge {{
                background: #FF6B35;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                display: inline-block;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                color: #888;
                font-size: 12px;
                margin-top: 20px;
                border-top: 1px solid #eee;
                padding-top: 20px;
            }}
            .total {{
                font-size: 24px;
                font-weight: bold;
                color: #FF6B35;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🍕 FoodHouse</h1>
                <p>Order Confirmation</p>
            </div>
            
            <h2>Thank you for your order, {customer_name}!</h2>
            <p>Your order has been placed successfully and is being processed.</p>
            
            <div class="order-details">
                <p><strong>Order ID:</strong> #{order_id}</p>
                <p><strong>Order Date:</strong> {order_date}</p>
                <p><strong>Status:</strong> <span class="status-badge">Pending</span></p>
            </div>
            
            <h3>Order Summary</h3>
            <div class="order-details">
                <p><strong>Products:</strong></p>
                <p>{product_names}</p>
                <p><strong>Total Amount:</strong> <span class="total">${total_amount}</span></p>
            </div>
            
            <h3>Delivery Details</h3>
            <div class="order-details">
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Phone:</strong> {phone}</p>
                <p><strong>Address:</strong> {address}</p>
            </div>
            
            <p>We'll notify you once your order is confirmed and out for delivery.</p>
            
            <div class="footer">
                <p>Thank you for choosing FoodHouse!</p>
                <p>If you have any questions, please contact us at support@FoodHouse.com</p>
                <p>&copy; 2025 FoodHouse. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    plain_text = f"""
    FoodHouse Order Confirmation
    
    Thank you for your order, {customer_name}!
    
    Order ID: #{order_id}
    Order Date: {order_date}
    Status: Pending
    
    Products: {product_names}
    Total Amount: ${total_amount}
    
    Delivery Details:
    Email: {email}
    Phone: {phone}
    Address: {address}
    
    We'll notify you once your order is confirmed.
    
    Thank you for choosing FoodHouse!
    """

    return html_body, plain_text

def generate_admin_notification_email(data):
    """
    Generate HTML email content for admin notification
    """
    customer_name = data.get('customer_name', 'Customer')
    order_id = data.get('order_id', 'N/A')
    product_names = data.get('products', '')
    total_amount = data.get('total_amount', '0.00')
    email = data.get('email', '')
    phone = data.get('phone', '')
    address = data.get('address', '')
    order_date = datetime.now().strftime('%B %d, %Y %I:%M %p')

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 10px 10px 0 0;
                margin: -30px -30px 20px -30px;
            }}
            .alert {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 15px 0;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛒 New Order Alert</h1>
                <p>FoodHouse Admin Notification</p>
            </div>
            
            <div class="alert">
                <strong>A new order has been placed!</strong>
            </div>
            
            <h3>Order Details</h3>
            <p><strong>Order ID:</strong> #{order_id}</p>
            <p><strong>Order Date:</strong> {order_date}</p>
            
            <h3>Customer Information</h3>
            <p><strong>Name:</strong> {customer_name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone}</p>
            <p><strong>Address:</strong> {address}</p>
            
            <h3>Order Summary</h3>
            <p><strong>Products:</strong> {product_names}</p>
            <p><strong>Total Amount:</strong> <strong>${total_amount}</strong></p>
            
            <p>Please review and confirm the order.</p>
            
            <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                <p>FoodHouse Admin Panel</p>
                <p style="color: #888; font-size: 12px;">This is an automated notification.</p>
            </div>
        </div>
    </body>
    </html>
    """

    plain_text = f"""
    New Order Alert
    
    A new order has been placed!
    
    Order ID: #{order_id}
    Order Date: {order_date}
    
    Customer: {customer_name}
    Email: {email}
    Phone: {phone}
    Address: {address}
    
    Products: {product_names}
    Total: ${total_amount}
    
    Please review and confirm the order.
    """

    return html_body, plain_text

def lambda_handler(event, context):
    """
    Main Lambda handler function - Handles both direct and API Gateway calls
    """
    try:
        logger.info("Received event: %s", json.dumps(event))
        
        # Parse request body - handle different event structures
        body = {}
        
        # Check if this is an API Gateway event
        if 'body' in event:
            # API Gateway wraps the body as a string
            if isinstance(event['body'], str):
                try:
                    body = json.loads(event['body'])
                except json.JSONDecodeError:
                    # If body is not JSON, try to parse it as a string
                    logger.error(f"Failed to parse body as JSON: {event['body']}")
                    body = {}
            else:
                body = event['body']
        else:
            # Direct Lambda invocation
            body = event
        
        # If body is empty, try to use the event itself
        if not body:
            body = event
        
        # Extract email data
        customer_email = body.get('customer_email')
        admin_email = body.get('admin_email', 'admin@FoodHouse.com')
        customer_name = body.get('customer_name', 'Customer')
        order_id = body.get('order_id', 'N/A')
        products = body.get('products', '')
        total_amount = body.get('total_amount', '0.00')
        phone = body.get('phone', '')
        address = body.get('address', '')
        
        logger.info(f"Processing order: {order_id} for customer: {customer_email}")
        logger.info(f"Customer name: {customer_name}")
        logger.info(f"Products: {products}")
        logger.info(f"Total: ${total_amount}")
        
        # Validate required fields
        if not customer_email:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Customer email is required'})
            }
        
        # Prepare data for email templates
        email_data = {
            'customer_name': customer_name,
            'order_id': order_id,
            'products': products,
            'total_amount': total_amount,
            'email': customer_email,
            'phone': phone,
            'address': address
        }
        
        # Generate email content for customer
        customer_html, customer_plain = generate_order_confirmation_email(email_data)
        
        # Send email to customer
        customer_success = send_smtp_email(
            to_email=customer_email,
            subject=f"Order Confirmation - FoodHouse #{order_id}",
            html_body=customer_html,
            plain_text_body=customer_plain
        )
        
        logger.info(f"Customer email sent: {customer_success}")
        
        # Generate email content for admin
        admin_html, admin_plain = generate_admin_notification_email(email_data)
        
        # Send email to admin
        admin_success = send_smtp_email(
            to_email=admin_email,
            subject=f"New Order Alert - FoodHouse #{order_id}",
            html_body=admin_html,
            plain_text_body=admin_plain
        )
        
        logger.info(f"Admin email sent: {admin_success}")
        
        # Return response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Email sent successfully',
                'customer_email_sent': customer_success,
                'admin_email_sent': admin_success
            })
        }
        
        logger.info("Response: %s", response)
        return response
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }