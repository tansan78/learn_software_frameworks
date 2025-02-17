"""
implement ths following functions:
- batch_write_table()
- get_customer_orders()
"""

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
    """
    TO BE IMPLEMENTED
    """
    df = pd.read_csv(CSV_FILE_LOCATION)
    
    with get_table().batch_writer() as writer:
        for _, row in df.iterrows():
            ### CODE HERE; and access content like row['customer_id'], row.get('order_id', '')
            ### row.get('product_name', ''), row.get('order_date', '')
            pass


def get_customer_orders(customer_id: str,
                        product_name_substr: Optional[str] =None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None):
    """
    TO BE IMPLEMENTED
    """


if __name__ == "__main__":
    main()
    