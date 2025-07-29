#!/bin/bash

# AlphaWolf AWS Deployment Script
set -e

echo "🐺 AlphaWolf Deployment Starting..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Run 'aws configure' first."
    exit 1
fi

# Set deployment stage
STAGE=${1:-dev}
REGION=${2:-us-east-1}

echo "📍 Deploying to stage: $STAGE in region: $REGION"

# Deploy serverless backend
echo "🚀 Deploying serverless backend..."
cd alphawolf
serverless deploy --stage $STAGE --region $REGION

# Get API Gateway URL
API_URL=$(serverless info --stage $STAGE --region $REGION | grep "ServiceEndpoint" | cut -d' ' -f2)
echo "✅ Backend deployed to: $API_URL"

# Return to root
cd ..

# Deploy web application (if using Elastic Beanstalk)
if command -v eb &> /dev/null; then
    echo "🌐 Deploying web application..."
    if [ ! -f .elasticbeanstalk/config.yml ]; then
        eb init alphawolf-web --region $REGION --platform python-3.11
    fi
    
    # Create or deploy
    if ! eb status > /dev/null 2>&1; then
        eb create alphawolf-web-$STAGE --instance-type t3.micro
    else
        eb deploy
    fi
    
    WEB_URL=$(eb status | grep "CNAME" | cut -d':' -f2 | xargs)
    echo "✅ Web app deployed to: http://$WEB_URL"
fi

echo "🎉 AlphaWolf deployment complete!"
echo "📊 Monitor at: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#dashboards:name=AlphaWolf-$STAGE"