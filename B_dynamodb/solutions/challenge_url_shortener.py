from typing import Optional
import os
import logging
import random
import base64

import boto3
import botocore

logging.basicConfig(level=logging.INFO)


SHORT_TO_FULL_TABLE_NAME = 'short_to_full_url_table'
FULL_TO_SHORT_TABLE_NAME = 'full_to_short_url_table'

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
short_to_full_table_obj = None
full_to_short_table_obj = None


def main():
    random.seed(1)

    # Create and nuke tables
    create_tables()

    # Load URLs
    urls = []
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'urls.txt')
    with open(file_path, 'r') as file:
        urls = [line.rstrip() for line in file]
    urls = list(filter(lambda x: x.startswith('http'), urls))

    logging.info('Add URLs....')
    num_urls_to_shorten = 200
    short_to_full_url_map = {}
    full_to_short_url_map = {}
    for i in range(num_urls_to_shorten):
        short_url = encode_n_save_url(urls[i])
        short_to_full_url_map[short_url] = urls[i]
        full_to_short_url_map[urls[i]] = short_url

        if i % 20 == 0:
            logging.info(f'Shortened {i} URLs')
    
    # let us encode a few URLs for the second time, to check that short URLs are not create twice for existing full URLs
    logging.info('Verify duplicated URLs....')
    for i in range(10):
        short_url = encode_n_save_url(urls[i])
        if short_url != full_to_short_url_map[urls[i]]:
            logging.error(f"Short URL is created twice for the same full URL {urls[i]}")
    
    # Look up a few short URLs
    logging.info('Verify shortened URLs....')
    all_short_urls = list(short_to_full_url_map.keys())
    for i in range(3):
        short_url = random.choice(all_short_urls)
        full_url = short_to_full_url_map[short_url]

        full_url_from_db = look_up_short_url(short_url)
        if full_url != full_url_from_db:
            logging.error(f"the short URL ({short_url}) lookup returns a different full URL: ({short_url}), ({full_url_from_db})")

    logging.info('MAIN process exiting...')


def create_short_to_full_table():
    global short_to_full_table_obj

    short_to_full_table_obj = ddb.Table(SHORT_TO_FULL_TABLE_NAME)
    try:
        short_to_full_table_obj.delete()
    except botocore.exceptions.ClientError:
        pass

    AttributeDefinitions = [
        { 'AttributeName': 'short_url', 'AttributeType': 'S'}
    ]
    KeySchema=[
        {'AttributeName': 'short_url', 'KeyType': 'HASH'},
    ]
    ProvisionedThroughput = {'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}

    short_to_full_table_obj = ddb.create_table(
        TableName=SHORT_TO_FULL_TABLE_NAME,
        AttributeDefinitions=AttributeDefinitions,
        KeySchema=KeySchema,
        ProvisionedThroughput=ProvisionedThroughput)
    short_to_full_table_obj.wait_until_exists()


def create_full_to_short_table():
    global full_to_short_table_obj

    full_to_short_table_obj = ddb.Table(FULL_TO_SHORT_TABLE_NAME)
    try:
        full_to_short_table_obj.delete()
    except botocore.exceptions.ClientError:
        pass

    AttributeDefinitions = [
        { 'AttributeName': 'full_url', 'AttributeType': 'S'}
    ]
    KeySchema=[
        {'AttributeName': 'full_url', 'KeyType': 'HASH'},
    ]
    ProvisionedThroughput = {'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}

    full_to_short_table_obj = ddb.create_table(
        TableName=FULL_TO_SHORT_TABLE_NAME,
        AttributeDefinitions=AttributeDefinitions,
        KeySchema=KeySchema,
        ProvisionedThroughput=ProvisionedThroughput)
    full_to_short_table_obj.wait_until_exists()


def create_tables():
    # Note when creating tables, we need to specify and only specify the attribute definition of keys; specifying
    # attributes of other fields will cause error;
    # Also, we need to specify ProvisionedThroughput even thoug we don't care here.
    create_short_to_full_table()
    create_full_to_short_table()


def encode_n_save_url(full_url: str) -> str:
    # Look up to check whether the full URL has been encoded before
    short_url = look_up_long_url(full_url)
    if short_url:
        return short_url

    # Look for a unused short URL
    encoded_short_url = None
    for i in range(5):
        rand_int = random.randint(0, 1000_0000_000)
        number_bytes = rand_int.to_bytes(8, 'big')
        encoded_short_url = base64.b64encode(number_bytes).decode('utf-8')

        stored_full_url = look_up_short_url(encoded_short_url)
        if not stored_full_url:
            break
        else:
            encoded_short_url = None

    if not encoded_short_url:
        logging.info('Unable to find a new available short URL')
        return None
    
    short_to_full_table_obj.put_item(Item={'short_url': encoded_short_url, 'full_url': full_url})
    full_to_short_table_obj.put_item(Item={'full_url': full_url, 'short_url': encoded_short_url})
    return encoded_short_url


def look_up_short_url(short_url: str) -> Optional[str]:
    short_to_full_table_obj = ddb.Table(SHORT_TO_FULL_TABLE_NAME)
    resp = short_to_full_table_obj.get_item(Key={'short_url': short_url})

    if 'Item' not in resp:
        return None
    
    return resp['Item']['full_url']


def look_up_long_url(full_url: str) -> Optional[str]:
    # Ideally we should normalize URL before lookup; however, to keep things simple, skip normalization
    full_to_short_table_obj = ddb.Table(FULL_TO_SHORT_TABLE_NAME)
    resp = full_to_short_table_obj.get_item(Key={'full_url': full_url})

    if 'Item' not in resp:
        return None
    return resp['Item']['short_url']


if __name__ == "__main__":
    main()