#!/bin/bash
# Azure deployment script for PHP + MySQL backend

# Variables
RESOURCE_GROUP="BeneficiaryRG"
APP_NAME="beneficiaryapp$RANDOM"
LOCATION="eastus"
MYSQL_SERVER="beneficiarymysql$RANDOM"
MYSQL_ADMIN="adminuser"
MYSQL_PASSWORD="StrongPassw0rd!"
DB_NAME="myproject_db"

# 1. Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create MySQL server
az mysql flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $MYSQL_SERVER \
  --admin-user $MYSQL_ADMIN \
  --admin-password $MYSQL_PASSWORD \
  --location $LOCATION \
  --public-access 0.0.0.0

# 3. Create database
az mysql flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $MYSQL_SERVER \
  --database-name $DB_NAME

# 4. Deploy PHP App Service
az webapp up \
  --runtime "PHP|8.1" \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# 5. Configure environment variables
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings DB_HOST="$MYSQL_SERVER.mysql.database.azure.com" DB_USER="$MYSQL_ADMIN" DB_PASS="$MYSQL_PASSWORD" DB_NAME="$DB_NAME"

echo "✅ Deployment complete. App URL: https://$APP_NAME.azurewebsites.net"
