import os

# SECURITY WARNING: keep the secret key used in production secret!
# Use this py command to create secret 
# python -c 'import secrets; print(secrets.token_hex())'
auth_token = os.getenv("huggingface-auth-token")
model_id = os.getenv("huggingface-model-id")
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")

# Configure allowed host names that can be served and trusted origins for Azure Container Apps.
ALLOWED_HOSTS = ['.azurecontainerapps.io'] if 'RUNNING_IN_PRODUCTION' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://*.azurecontainerapps.io'] if 'RUNNING_IN_PRODUCTION' in os.environ else []
DEBUG = False

# Configure database connection for Azure PostgreSQL Flexible server instance.
# AZURE_POSTGRESQL_HOST is the full URL.
# AZURE_POSTGRESQL_USERNAME is just name without @server-name.
DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ['AZURE_POSTGRESQL_USERNAME'],
    dbpass=os.environ['AZURE_POSTGRESQL_PASSWORD'],
    dbhost=os.environ['AZURE_POSTGRESQL_HOST'],
    dbname=os.environ['AZURE_POSTGRESQL_DATABASE']
)


