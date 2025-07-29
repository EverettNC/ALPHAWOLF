# AlphaWolf AWS Deployment Setup

## Prerequisites

1. **AWS Account Setup**
   ```bash
   # Install AWS CLI
   curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
   sudo installer -pkg AWSCLIV2.pkg -target /
   
   # Configure AWS credentials
   aws configure
   ```

2. **Install Serverless Framework**
   ```bash
   npm install -g serverless
   npm install -g serverless-python-requirements
   npm install -g serverless-dotenv-plugin
   npm install -g serverless-iam-roles-per-function
   ```

## Environment Variables Setup

Create `.env` file in your root directory:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id

# Database
DATABASE_URL=your-production-db-url

# Security
SESSION_SECRET=your-secure-session-secret

# Alerts
ALERT_NOTIFICATION_EMAIL=your-email@domain.com

# Risk Thresholds
HIGH_RISK_THRESHOLD=0.7
MEDIUM_RISK_THRESHOLD=0.4

# Content Crawler
CONTENT_CRAWLER_ENABLED=true
MAX_CACHE_AGE_DAYS=7

# Logging
LOG_LEVEL=INFO
```

## Deployment Steps

### 1. Prepare Lambda Layer
```bash
cd alphawolf
mkdir -p layer/python
pip install -r requirements.txt -t layer/python/
```

### 2. Deploy Serverless Stack
```bash
cd alphawolf
serverless deploy --stage prod --region us-east-1
```

### 3. Deploy Web Application
For the Flask web app, you'll need additional setup:

#### Option A: AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize and deploy
eb init alphawolf-web
eb create alphawolf-web-prod
eb deploy
```

#### Option B: AWS App Runner (Recommended)
```bash
# Create apprunner.yaml in root
```

## Database Setup

### Option A: Amazon RDS (PostgreSQL)
```bash
# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier alphawolf-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username alphawolf \
    --master-user-password your-secure-password \
    --allocated-storage 20
```

### Option B: Amazon DynamoDB (Already configured in serverless.yml)
Your serverless config already includes DynamoDB tables.

## Static Assets (S3 + CloudFront)

```bash
# Create S3 bucket for static assets
aws s3 mb s3://alphawolf-static-assets

# Upload static files
aws s3 sync static/ s3://alphawolf-static-assets/static/

# Create CloudFront distribution (optional)
```

## Security Setup

1. **IAM Roles** - Already configured in serverless.yml
2. **VPC Configuration** (if needed)
3. **SSL Certificate** via AWS Certificate Manager

## Monitoring & Logging

Your serverless.yml already includes:
- CloudWatch Dashboard
- Log retention
- SNS alerts

## Cost Optimization

1. **Lambda**: Pay per invocation
2. **DynamoDB**: On-demand billing
3. **S3**: Lifecycle policies configured
4. **CloudWatch**: Log retention set to 30 days

## Post-Deployment

1. **Test API endpoints**
2. **Configure domain name**
3. **Set up monitoring alerts**
4. **Configure backup strategies**