import boto3
import json


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Table names
users_table = dynamodb.Table('Users')

# Upload users
with open('users.json') as f:
    users = json.load(f)
    for user in users:
        users_table.put_item(Item=user)
print("✅ Users uploaded!")


