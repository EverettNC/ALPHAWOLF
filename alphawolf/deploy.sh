#!/bin/bash
#
# AlphaWolf Deployment Script
# Part of The Christman AI Project - LumaCognify AI
#
# This script deploys the AlphaWolf serverless infrastructure to AWS.
#
# "HOW CAN I HELP YOU LOVE YOURSELF MORE"
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "==============================================================="
echo " _    _     ___  _  _    _        __      __   _    ___"
echo "/ \\  | |   | _ \\| || |  / \\      /  \\    / __| | |  | __|"
echo "/ _ \\ | |__ |  _/| __ | / _ \\    / /\\ \\  | (__  | |__| _|"
echo "/_/ \\_\\|____||_|  |_||_|/_/ \\_\\  /_/  \\_\\  \\___| |____|_|"
echo ""
echo "Part of The Christman AI Project - LumaCognify AI"
echo "==============================================================="
echo -e "${NC}"

# Configuration
STACK_NAME="alphawolf"
STAGE=${1:-"dev"}
REGION=${2:-"us-east-1"}
PROFILE=${3:-"default"}

# Check dependencies
command -v aws >/dev/null 2>&1 || { echo -e "${RED}Error: AWS CLI is required but not installed.${NC}" >&2; exit 1; }
command -v serverless >/dev/null 2>&1 || { echo -e "${RED}Error: Serverless Framework is required but not installed.${NC}" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo -e "${RED}Error: jq is required but not installed.${NC}" >&2; exit 1; }

echo -e "${BLUE}Deploying AlphaWolf to ${YELLOW}${STAGE}${BLUE} environment in ${YELLOW}${REGION}${BLUE} region...${NC}"

# Validate AWS credentials
echo -e "${BLUE}Validating AWS credentials...${NC}"
aws sts get-caller-identity --profile ${PROFILE} > /dev/null || { echo -e "${RED}Error: Invalid AWS credentials.${NC}" >&2; exit 1; }
echo -e "${GREEN}AWS credentials validated.${NC}"

# Create S3 deployment bucket if it doesn't exist
DEPLOYMENT_BUCKET="alphawolf-serverless-${STAGE}"
echo -e "${BLUE}Checking if deployment bucket exists: ${YELLOW}${DEPLOYMENT_BUCKET}${NC}"
if ! aws s3api head-bucket --bucket ${DEPLOYMENT_BUCKET} --profile ${PROFILE} 2>/dev/null; then
    echo -e "${BLUE}Creating deployment bucket...${NC}"
    aws s3api create-bucket --bucket ${DEPLOYMENT_BUCKET} --profile ${PROFILE} --region ${REGION}
    
    # Enable versioning
    aws s3api put-bucket-versioning --bucket ${DEPLOYMENT_BUCKET} --versioning-configuration Status=Enabled --profile ${PROFILE}
    
    # Add encryption
    aws s3api put-bucket-encryption --bucket ${DEPLOYMENT_BUCKET} --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}' --profile ${PROFILE}
    
    echo -e "${GREEN}Deployment bucket created and configured.${NC}"
else
    echo -e "${GREEN}Deployment bucket already exists.${NC}"
fi

# Check for required files
echo -e "${BLUE}Validating project files...${NC}"
if [ ! -f "serverless.yml" ]; then
    echo -e "${RED}Error: serverless.yml not found.${NC}" >&2
    exit 1
fi

# Create or update environment variables file
ENV_FILE=".env.${STAGE}.json"
echo -e "${BLUE}Checking environment variables file: ${YELLOW}${ENV_FILE}${NC}"
if [ ! -f "${ENV_FILE}" ]; then
    echo -e "${YELLOW}Environment file not found. Creating a new one...${NC}"
    cat << EOF > ${ENV_FILE}
{
  "STAGE": "${STAGE}",
  "REGION": "${REGION}",
  "LOG_LEVEL": "INFO",
  "ALERT_NOTIFICATION_EMAIL": "alerts@example.com",
  "MAX_CACHE_AGE_DAYS": "7",
  "CONTENT_CRAWLER_ENABLED": "true",
  "HIGH_RISK_THRESHOLD": "0.7",
  "MEDIUM_RISK_THRESHOLD": "0.4"
}
EOF
    echo -e "${GREEN}Environment file created. Please update with actual values.${NC}"
    echo -e "${YELLOW}Would you like to continue with default values? (y/n)${NC}"
    read -r CONTINUE
    if [[ $CONTINUE != "y" ]]; then
        echo -e "${YELLOW}Deployment aborted. Please update ${ENV_FILE} and try again.${NC}"
        exit 0
    fi
else
    echo -e "${GREEN}Environment file found.${NC}"
fi

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt --target ./package > /dev/null
echo -e "${GREEN}Dependencies installed.${NC}"

# Build package
echo -e "${BLUE}Building deployment package...${NC}"
cd package
zip -r9 ../function.zip . > /dev/null
cd ..
zip -g function.zip -r api/ core/ data/ utils/ > /dev/null
echo -e "${GREEN}Deployment package built.${NC}"

# Run tests
echo -e "${BLUE}Running tests...${NC}"
python -m unittest test_lambda.py
echo -e "${GREEN}Tests passed.${NC}"

# Deploy with Serverless Framework
echo -e "${BLUE}Deploying to AWS...${NC}"
serverless deploy --stage ${STAGE} --region ${REGION} --aws-profile ${PROFILE} --verbose

# Verify deployment
echo -e "${BLUE}Verifying deployment...${NC}"
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME}-${STAGE} --profile ${PROFILE} --region ${REGION} --query "Stacks[0].StackStatus" --output text)

if [[ $STACK_STATUS == *"COMPLETE"* ]]; then
    echo -e "${GREEN}Deployment successful!${NC}"
    
    # Get API endpoint
    API_URL=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME}-${STAGE} --profile ${PROFILE} --region ${REGION} --query "Stacks[0].Outputs[?OutputKey=='ServiceEndpoint'].OutputValue" --output text)
    
    echo -e "${GREEN}AlphaWolf API is available at:${NC}"
    echo -e "${BLUE}${API_URL}${NC}"
    
    # Show available endpoints
    echo -e "${GREEN}Available endpoints:${NC}"
    echo -e "${YELLOW}POST ${API_URL}/analyze-risk${NC} - Analyzes risk in input text"
    echo -e "${YELLOW}POST ${API_URL}/check-location${NC} - Checks location safety"
    echo -e "${YELLOW}POST ${API_URL}/get-research${NC} - Retrieves latest research"
    echo -e "${YELLOW}GET ${API_URL}/health${NC} - API health check"
    
    # Clean up
    echo -e "${BLUE}Cleaning up temporary files...${NC}"
    rm -rf package/
    rm function.zip
    
    echo -e "${GREEN}Deployment complete!${NC}"
else
    echo -e "${RED}Deployment failed. Stack status: ${STACK_STATUS}${NC}"
    echo -e "${YELLOW}Check CloudFormation console for more details.${NC}"
    exit 1
fi