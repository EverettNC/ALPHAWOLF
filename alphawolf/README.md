# AlphaWolf: Cognitive Care & Family Protection AI

Part of The Christman AI Project - LumaCognify AI

## "HOW CAN I HELP YOU LOVE YOURSELF MORE"

![AlphaWolf Logo](../static/images/alphawolf-logo.svg)

## Overview

AlphaWolf is a comprehensive AI-powered platform supporting neurodivergent individuals, with a focus on assistive technologies for cognitive care, safety, and personal empowerment for those with Alzheimer's and dementia. 

AlphaWolf is a spiritual sibling to AlphaVox (a multi-modal neurodiverse inclusive speech-generating artificial intelligence designed for nonverbal autistic individuals), adapted specifically for dementia and Alzheimer's care applications.

## Core Modules

### Family Protection System
The Family Protection System monitors safety through geofencing, location monitoring, and risk assessment. Key features include:

- **Geofencing**: Define safe zones and receive alerts when a person leaves these areas
- **Unusual Movement Detection**: Identify potentially dangerous movement patterns
- **Risk Communication Analysis**: Detect concerning language in communications

### Web Crawler
The Web Crawler retrieves authoritative information about Alzheimer's and dementia from trusted sources:

- **Topic Search**: Find relevant information on specific topics
- **Research Retrieval**: Access the latest research on dementia conditions
- **Fact Extraction**: Extract factual statements from content

### Content Filtering & Risk Analysis
Content processing with risk assessment:

- **Message Risk Analysis**: Evaluate input for concerning content
- **Safety Reporting**: Generate comprehensive safety reports
- **Alert Generation**: Produce structured alerts for potential safety issues

## Serverless Architecture

AlphaWolf is built as a serverless application on AWS with the following components:

- **API Gateway**: Edge-optimized, handling all API requests
- **Lambda Functions**: Serverless compute for all processing
- **DynamoDB**: NoSQL storage for interaction history, locations, and content
- **SQS**: Message queuing for alerts and asynchronous processing
- **S3**: Storage for static content and data
- **CloudWatch**: Monitoring and logging

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analyze` | POST | Analyze input for risk factors |
| `/api/v1/safety` | POST | Check location safety relative to defined zones |
| `/api/v1/track` | POST | Analyze movement patterns for unusual activity |
| `/api/v1/protection` | POST | Family protection features including geofencing |
| `/api/v1/risk` | POST | Risk analysis of user input |
| `/api/v1/content` | GET | Retrieve information on specific topics |
| `/api/v1/research` | GET | Access latest research on conditions |
| `/health` | GET | Service health check |

## Deployment

AlphaWolf is deployed using the Serverless Framework. To deploy:

1. Install dependencies: `npm install -g serverless`
2. Configure AWS credentials
3. Run deployment script: `./deploy.sh [stage] [region] [profile]`

### Example deployment:
```bash
# Deploy to dev environment in us-east-1 using default profile
./deploy.sh dev us-east-1 default

# Deploy to production
./deploy.sh prod us-east-1 production
```

## Development

### Prerequisites
- Python 3.11+
- AWS CLI
- Serverless Framework
- Node.js 16+

### Local Development
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run local tests: `python -m unittest discover tests`
4. Start local API: `serverless offline`

## Security & Compliance

AlphaWolf is designed with security and privacy in mind:

- All data is encrypted at rest and in transit
- User data is anonymized where possible
- Compliance with healthcare privacy standards
- Regular security audits

## Contact

For questions or support:
- Email: research@lumacognify.ai
- Website: https://alphawolf.christmanai.org