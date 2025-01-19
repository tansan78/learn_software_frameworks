import os 
import logging
from dateutil import parser
import random

import boto3
import botocore
import pandas as pd


logging.basicConfig(level=logging.INFO)


TABLE_NAME = 'ecommerce'
CSV_FILE_LOCATION = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 'data', 'Ecommerce_data.csv')

# ddb = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
table_obj = None
 

def main():
    # delete_table()
    # create_table()
    batch_write_table()


def delete_table():
    try:
        get_table().load()
    except botocore.exceptions.ClientError as err:
        if err.response["Error"]["Code"] == "ResourceNotFoundException":
            return
        else:
            logging.exception('Failed to load table', err)
            return
    
    get_table().delete()


def batch_write_table():
    df = pd.read_csv(CSV_FILE_LOCATION)
    # different customer_id has different name and city/state; let us fix it
    # this is not necessary though
    transform_cols = ['customer_first_name', 'customer_last_name', 'customer_segment',
                      'customer_city', 'customer_state']
    df.update(
        df.groupby('customer_id')[transform_cols].transform('first')
    )

    # selected_df = df.sample(n=100)
    added_customer_id = set()
    added_order_id = set()
    selected_df = df
    with get_table().batch_writer() as writer:
        for _, row in selected_df.iterrows():
            # logging.info(f'Write record for user id: {row['customer_id']}')
            if row['customer_id'] not in added_customer_id:
                writer.put_item(Item=create_customer_item(
                    customer_id=row['customer_id'],
                    customer_first_name=row.get('customer_first_name', ''),
                    customer_last_name=row.get('customer_last_name', ''),
                    customer_segment=row.get('customer_segment', ''),
                    customer_city=row.get('customer_city', ''),
                    customer_state=row.get('customer_state', ''),
                ))
                added_customer_id.add(row['customer_id'])

            if row.get('order_id', '') not in added_order_id:
                writer.put_item(Item=create_order_item(
                    customer_id=row['customer_id'],
                    order_id=row.get('order_id', ''),
                    product_name=row.get('product_name', ''),
                    order_date=row.get('order_date', ''),
                    ship_date=row.get('ship_date', ''),
                ))
                added_order_id.add(row.get('order_id', ''))
    logging.info(f'Completed writing records; total record: {df.shape[0]}; written customer: {len(added_customer_id)}'
                 + f'written orders: {len(added_order_id)}')

def write_table():
    df = pd.read_csv(CSV_FILE_LOCATION)
    
    index = random.randint(0, df.shape[0])
    logging.info(f'Write record for index {index}, with user id: {df.iloc[index]['customer_id']}')
    row = df.iloc[index, :]

    get_table().put_item(Item=create_customer_item(
        customer_id=row['customer_id'],
        customer_first_name=row.get('customer_first_name', ''),
        customer_last_name=row.get('customer_last_name', ''),
        customer_segment=row.get('customer_segment', ''),
        customer_city=row.get('customer_city', ''),
        customer_state=row.get('customer_state', ''),
    ))

    get_table().put_item(Item=create_order_item(
        customer_id=row['customer_id'],
        order_id=row.get('order_id', ''),
        product_name=row.get('product_name', ''),
        order_date=row.get('order_date', ''),
        ship_date=row.get('ship_date', ''),
    ))


def get_table():
    global table_obj
    if not table_obj:
        table_obj = ddb.Table(TABLE_NAME)
    return table_obj


def create_customer_item(customer_id, customer_first_name, customer_last_name,
                        customer_segment, customer_city, customer_state):
    return {
        'customer_id': customer_id,
        'order_date_plus_order_id': 'customer_info',
        'name': {"first_name": customer_first_name, "last_name": customer_last_name},
        'customer_segment': customer_segment,
        'address': {"city": customer_city, "state": customer_state}
    }


def create_order_item(customer_id, order_id, product_name, order_date, ship_date):
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
        'order_date': order_date,
        'ship_date': ship_date
    }


def create_table():
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

    ProvisionedThroughput = { 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}

    try:
        table = ddb.create_table(TableName=TABLE_NAME,
                                    AttributeDefinitions=AttributeDefinitions,
                                    KeySchema=KeySchema,
                                    LocalSecondaryIndexes=LocalSecondaryIndexes,
                                    ProvisionedThroughput=ProvisionedThroughput
                                    )
        table.wait_until_exists()
    except ddb.exceptions.ResourceInUseException:
        logging.info(f'Table "{TABLE_NAME}" already exists')
            

if __name__ == "__main__":
    main()
    