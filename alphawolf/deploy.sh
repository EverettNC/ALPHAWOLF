#!/bin/bash
###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# DEPLOYMENT SCRIPT
# Deploy the AlphaWolf serverless infrastructure to AWS
###############################################################################

# Set defaults
STAGE=${1:-dev}
REGION=${2:-us-east-1}

echo "==============================================================="
echo "AlphaWolf Deployment - LumaCognify AI"
echo "The Christman AI Project"
echo "==============================================================="
echo "Deploying to stage: $STAGE"
echo "Region: $REGION"
echo "==============================================================="

# Check for AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Error: AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
    exit 1
fi

# Check for Serverless Framework
if ! command -v serverless &> /dev/null; then
    echo "Serverless Framework not found. Installing..."
    npm install -g serverless
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Serverless plugins
echo "Installing Serverless plugins..."
serverless plugin install -n serverless-python-requirements
serverless plugin install -n serverless-plugin-aws-alerts
serverless plugin install -n serverless-plugin-tracing

# Deploy using Serverless Framework
echo "Deploying with Serverless Framework..."
serverless deploy --stage $STAGE --region $REGION

# Check deployment result
if [ $? -eq 0 ]; then
    echo "==============================================================="
    echo "Deployment successful!"
    echo "==============================================================="
    serverless info --stage $STAGE --region $REGION
    exit 0
else
    echo "==============================================================="
    echo "Deployment failed. Check the logs above for details."
    echo "==============================================================="
    exit 1
fi