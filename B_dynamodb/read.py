from typing import Optional
import os 
import logging
from datetime import datetime

import boto3
import pandas as pd


logging.basicConfig(level=logging.INFO)


TABLE_NAME = 'ecommerce'
CSV_FILE_LOCATION = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 'data', 'Ecommerce_data.csv')

# ddb = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
table_obj = None
 

def main():
    customer_id = 'C_ID_36240'
    # this customer has 6 orders, with dates of:
    #    21-01-2022: 'Tyvek  Top-Opening Peel & Seel Envelopes, Plain White'
    #    8/8/2022:   'Ooma Telo VoIP Home Phone System'
    #    11/3/2022:  'Wirebound Message Books, Four 2 3/4 x 5 Forms per Page, 200 Sets per Book'
    #    11/5/2022:  'DAX Value U-Channel Document Frames, Easel Back'
    #    11/10/2022: 'Acme Forged Steel Scissors with Black Enamel Handles'

    get_customer_info(customer_id)
    
    start_date = datetime(year=2022, month=8, day=5)
    end_date = datetime(year=2022, month=11, day=8)
    logging.info(f'User {customer_id}\'s order from {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}')
    get_customer_orders(customer_id, start_date=start_date, end_date=end_date)
    
    product_name_substr = 'Phone'
    logging.info(f"User {customer_id}'s order with the word '{product_name_substr}' in product name")
    get_customer_orders(customer_id, product_name_substr=product_name_substr)


def get_customer_info(customer_id):
    return get_table().get_item(
        Key={
        'customer_id': customer_id,
        'order_date_plus_order_id': 'customer_info'
        },
        ExpressionAttributeNames={"#name": "name"},
        ProjectionExpression='#name.first_name, customer_id, customer_segment, address',
    )['Item']


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


def get_table():
    global table_obj
    if not table_obj:
        table_obj = ddb.Table(TABLE_NAME)
    return table_obj

            

if __name__ == "__main__":
    main()
    