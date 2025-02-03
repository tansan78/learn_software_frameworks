from typing import Optional
import os 
import logging
from dateutil import parser
from datetime import datetime

import boto3
import botocore
import pandas as pd


logging.basicConfig(level=logging.INFO)


TABLE_NAME = 'ecommerce'
CSV_FILE_LOCATION = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 'data', 'ecommerce.csv')

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
table_obj = None
 

def main():
    delete_table()
    create_table()
    batch_write_table()

    customer_id = 'C_ID_36240'
    # this customer has 6 orders, with dates of:
    #    21-01-2022: 'Tyvek  Top-Opening Peel & Seel Envelopes, Plain White'
    #    8/8/2022:   'Ooma Telo VoIP Home Phone System'
    #    11/3/2022:  'Wirebound Message Books, Four 2 3/4 x 5 Forms per Page, 200 Sets per Book'
    #    11/5/2022:  'DAX Value U-Channel Document Frames, Easel Back'
    #    11/10/2022: 'Acme Forged Steel Scissors with Black Enamel Handles'

    start_date = datetime(year=2022, month=8, day=5)
    end_date = datetime(year=2022, month=11, day=8)
    logging.info(f'User {customer_id}\'s order from {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}')
    get_customer_orders(customer_id, start_date=start_date, end_date=end_date)
    
    product_name_substr = 'Phone'
    logging.info(f"User {customer_id}'s order with the word '{product_name_substr}' in product name")
    get_customer_orders(customer_id, product_name_substr=product_name_substr)


def delete_table():
    table_obj = ddb.Table(TABLE_NAME)
    try:
        table_obj.load()
    except botocore.exceptions.ClientError:
        return
    
    table_obj.delete()


def create_table():
    global table_obj

    AttributeDefinitions = [
        { 'AttributeName': 'customer_id', 'AttributeType': 'S'},
        { 'AttributeName': 'order_date_plus_order_id', 'AttributeType': 'S'},
        { 'AttributeName': 'product_name', 'AttributeType': 'S'},
    ]
    KeySchema=[
        {'AttributeName': 'customer_id', 'KeyType': 'HASH'},
        {'AttributeName': 'order_date_plus_order_id', 'KeyType': 'RANGE'},
    ]
    LocalSecondaryIndexes=[
        {
            'IndexName': 'product_name',
            'KeySchema': [
                {'AttributeName': 'customer_id', 'KeyType': 'HASH'},
                {'AttributeName': 'product_name', 'KeyType': 'RANGE'},
            ],
            'Projection': { 'ProjectionType': 'KEYS_ONLY' }
        },
    ]
    ProvisionedThroughput = {'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}

    table_obj = ddb.create_table(TableName=TABLE_NAME,
                                AttributeDefinitions=AttributeDefinitions,
                                KeySchema=KeySchema,
                                LocalSecondaryIndexes=LocalSecondaryIndexes,
                                ProvisionedThroughput=ProvisionedThroughput)
    table_obj.wait_until_exists()
            

def get_table():
    global table_obj
    return table_obj


def batch_write_table():
    df = pd.read_csv(CSV_FILE_LOCATION)
    
    # selected_df = df.sample(n=100)
    added_order_id = set()
    with get_table().batch_writer() as writer:
        for _, row in df.iterrows():
            if row.get('order_id', '') not in added_order_id:
                writer.put_item(Item=create_order_item(
                    customer_id=row['customer_id'],
                    order_id=row.get('order_id', ''),
                    product_name=row.get('product_name', ''),
                    order_date=row.get('order_date', '')
                ))
                added_order_id.add(row.get('order_id', ''))

    logging.info(f'Completed writing records; total record: {df.shape[0]}; written orders: {len(added_order_id)}')


def create_order_item(customer_id, order_id, product_name, order_date):
    try:
        parsed_order_date = parser.parse(order_date)
        order_date_formatted_str = parsed_order_date.strftime("%Y-%m-%d")
    except parser.ParserError as e:
        logging.warning(f'Invalid order_date string "{order_date}" for order {order_id}')
        return None

    order_date_plus_order_id = f'order_{order_date_formatted_str}_{order_id}'
    return {
        'customer_id': customer_id,
        'order_id': order_id,
        'order_date_plus_order_id': order_date_plus_order_id,
        'product_name': product_name,
        'order_date': order_date
    }


def get_customer_orders(customer_id: str,
                        product_name_substr: Optional[str] =None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None):
    from boto3.dynamodb.conditions import Key, Attr

    KeyConditionExpression = Key("customer_id").eq(customer_id)

    # construct range date date filtering on sort key
    start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None
    if start_date_str and end_date_str:
        KeyConditionExpression = KeyConditionExpression & \
            Key("order_date_plus_order_id").between(f'order_{start_date_str}', f'order_{end_date_str}')
    elif start_date_str:
        KeyConditionExpression = KeyConditionExpression & Key("order_date_plus_order_id").gte(f'order_{start_date_str}')
    elif end_date_str:
        KeyConditionExpression = KeyConditionExpression & Key("order_date_plus_order_id").lte(f'order_{end_date_str}')

    result = get_table().query(
        KeyConditionExpression=KeyConditionExpression,
        FilterExpression=Attr("product_name").contains(product_name_substr if product_name_substr else ''),
        ProjectionExpression='order_date_plus_order_id, product_name, order_date',
    )
    
    for order in result['Items']:
        logging.info(f' - order: {order}')
    logging.info('\n')


if __name__ == "__main__":
    main()
    