#!/bin/bash
# AWS deployment script for PHP + MySQL backend

# Variables
APP_NAME="beneficiaryapp"
DB_INSTANCE="beneficiarydb"
DB_USER="adminuser"
DB_PASS="StrongPassw0rd!"
DB_NAME="myproject_db"
REGION="us-east-1"

# 1. Create RDS MySQL instance
aws rds create-db-instance \
  --db-instance-identifier $DB_INSTANCE \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username $DB_USER \
  --master-user-password $DB_PASS \
  --allocated-storage 20 \
  --region $REGION

echo "⏳ Waiting for RDS instance to be available..."
aws rds wait db-instance-available --db-instance-identifier $DB_INSTANCE

# 2. Create Elastic Beanstalk app
eb init -p php-8.1 $APP_NAME --region $REGION
eb create ${APP_NAME}-env

# 3. Set environment variables
eb setenv DB_HOST="${DB_INSTANCE}.xxxxx.rds.amazonaws.com" DB_USER="$DB_USER" DB_PASS="$DB_PASS" DB_NAME="$DB_NAME"

# 4. Deploy app
eb deploy

echo "✅ Deployment complete. App URL: $(eb status | grep 'CNAME' | awk '{print $2}')"
