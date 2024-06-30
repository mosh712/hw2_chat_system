import boto3
from botocore.exceptions import ClientError
from config import config

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=config.DYNAMODB_ENDPOINT_URL,
    region_name=config.DYNAMODB_REGION
)

def create_table(table_name, key_schema, attribute_definitions, provisioned_throughput):
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table {table_name} created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists.")
        else:
            print(f"Unexpected error: {e}")

def init_db():
    create_table(
            table_name='users',
            key_schema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'
                }
            ],
            attribute_definitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                }
            ],
            provisioned_throughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    create_table(
        table_name='messages',
        key_schema=[
            {
                'AttributeName': 'message_id',
                'KeyType': 'HASH'
            }
        ],
        attribute_definitions=[
            {
                'AttributeName': 'message_id',
                'AttributeType': 'S'
            }
        ],
        provisioned_throughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    create_table(
        table_name='chat_metadata',
        key_schema=[
            {
                'AttributeName': 'chat_id',
                'KeyType': 'HASH'
            }
        ],
        attribute_definitions=[
            {
                'AttributeName': 'chat_id',
                'AttributeType': 'S'
            }
        ],
        provisioned_throughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    create_table(
        table_name='group_members',
        key_schema=[
            {
                'AttributeName': 'group_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'user_id',
                'KeyType': 'RANGE'
            }
        ],
        attribute_definitions=[
            {
                'AttributeName': 'group_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'user_id',
                'AttributeType': 'S'
            }
        ],
        provisioned_throughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    create_table(
        table_name='groups',
        key_schema=[
            {
                'AttributeName': 'group_id',
                'KeyType': 'HASH'
            }
        ],
        attribute_definitions=[
            {
                'AttributeName': 'group_id',
                'AttributeType': 'S'
            }
        ],
        provisioned_throughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    create_table(
        table_name='blocks',
        key_schema=[
            {
                'AttributeName': 'block_id',
                'KeyType': 'HASH'
            }
        ],
        attribute_definitions=[
            {
                'AttributeName': 'block_id',
                'AttributeType': 'S'
            }
        ],
        provisioned_throughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
