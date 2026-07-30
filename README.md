# FoodHouse – Cloud-Native Online Food Ordering System

## Overview

FoodHouse is a cloud-based food ordering and delivery application developed using Django and AWS Cloud Services. The platform allows customers to browse food items, place orders online, receive invoices, and provide feedback, while administrators can manage products, customers, and orders through a centralized dashboard.

The application demonstrates cloud-native development using multiple AWS services and a custom Python package.

---

## Features

### Customer Features

* User Registration and Login
* Browse Food Menu
* Add Items to Cart
* Place Orders Online
* View Order Details
* Download Invoice
* Submit Feedback

### Administrator Features

* Manage Food Products
* Manage Customers
* Manage Orders
* View Customer Feedback
* Receive Order Notifications
* Monitor Business Activities

---

## Cloud Services Used

| AWS Service           | Purpose                        |
| --------------------- | ------------------------------ |
| Amazon S3             | Store food product images      |
| Amazon SNS            | Send order notification emails |
| Amazon SQS            | Queue-based message processing |
| AWS Lambda            | Serverless invoice processing  |
| Amazon API Gateway    | Invoke Lambda functions        |
| Amazon ECR            | Store Lambda container images  |
| Amazon RDS PostgreSQL | Database management            |
| AWS Elastic Beanstalk | Application deployment         |
| AWS Cloud9            | Development environment        |

---

## Custom Python Library

### invoice-pdf-lib

A custom PyPI package developed for this project.

Features:

* Generate unique invoice numbers
* Create PDF invoices
* Reusable invoice generation functionality
* Simplified invoice management

---

## Technology Stack

* Python
* Django
* PostgreSQL
* AWS Cloud Services
* HTML
* CSS
* Bootstrap
* GitHub Actions


---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd foodhouse
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Database Migrations

```bash
python manage.py migrate
```

### Start Application

```bash
python manage.py runserver
```

---

## Project Structure

```text
foodhouse/
│
├── app/
├── templates/
├── static/
├── media/
├── invoice_pdf_lib/
├── requirements.txt
├── manage.py
└── README.md
```

---

## CI/CD Deployment

GitHub Actions is used to automate Continuous Integration and Continuous Deployment (CI/CD).

Whenever code changes are pushed to GitHub, the application is automatically deployed to AWS Elastic Beanstalk.



---

## Author

Pooja

Cloud Platform Programming Project


