'''
This is to simulate the coupon system.
- a promotion allows certain amount of coupons
- every user can sign up at most once and get one coupon
'''
import logging
import time
import random 

from multiprocessing import Process

import pymysql


# The topic has 3 partitions defined in docker-compose.yml
NUM_PROCESSES = 3

DB_NAME = 'testdb'
RROMO_TABLE = 'promotions'
USER_COUPON_TABLE = 'user_coupons'
RPOMO_ID = '123456'

logging.basicConfig(level=logging.INFO)


def get_left_coupons(conn):
    with conn.cursor() as cursor:
        fetch_left_coupons = f"""
            SELECT left_coupons from `{DB_NAME}`.`{RROMO_TABLE}`
            WHERE promo_id = %(promo_id)s;
        """
        cursor.execute(fetch_left_coupons, {'promo_id': RPOMO_ID})
        left_coupon = cursor.fetchone()['left_coupons']
    
    return left_coupon


def get_user_coupon_num(conn):
    with conn.cursor() as cursor:
        get_user_record = f"""
            SELECT count(*) as cnt from `{DB_NAME}`.`{USER_COUPON_TABLE}`
            WHERE promo_id = %(promo_id)s;
        """

        cursor.execute(get_user_record, {'promo_id': RPOMO_ID})
        num_user_coupons = cursor.fetchone()['cnt']
    
    return num_user_coupons


def consumer_process(process_id):
    '''
    Worker process. There are multi worker processes; and each worker process is supposed to be
    responsible for a segment of the ring of consistent hashing.
    '''
    def user_generator():
        random.seed(process_id)
        last_user_id = None
        for i in range(150):
            # return the same ID with 10% chance
            if last_user_id and random.uniform(0, 1) < 0.1:
                logging.info(f'Process {process_id}: Emit a duplicated user ID {last_user_id}')
                yield last_user_id
            else:
                last_user_id = str(random.randint(0, 1000_000_000))
                yield last_user_id

    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='example',
                           database=DB_NAME,
                           cursorclass=pymysql.cursors.DictCursor)
    for rand_user in user_generator():
        left_coupon = get_left_coupons(conn)
        if left_coupon <= 0:
            logging.info(f'Process {process_id} found that no more left coupons in promo')
            break

        decrement_coupons = f"""
            UPDATE `{DB_NAME}`.`{RROMO_TABLE}` SET left_coupons = left_coupons - 1
            WHERE promo_id = %(promo_id)s ;
        """
        add_user_coupon = f"""
            INSERT `{DB_NAME}`.`{USER_COUPON_TABLE}` (user_id, promo_id, process_id)
            SELECT %(user_id)s, %(promo_id)s, {process_id}
            FROM `{DB_NAME}`.`{RROMO_TABLE}`
            WHERE left_coupons >= 0 ;
        """

        with conn.cursor() as cursor:
            cursor.execute(decrement_coupons, {'promo_id': RPOMO_ID, 'user_id': rand_user})
            try:
                cursor.execute(add_user_coupon, {'promo_id': RPOMO_ID, 'user_id': rand_user})
                conn.commit()
            except pymysql.err.IntegrityError as e:
                conn.rollback()
                logging.warning(f'Process {process_id}: Duplicated user found: {rand_user}')
        
        sleep_time = random.uniform(0.1, 1.0)
        time.sleep(sleep_time)
    
    logging.info(f'Process {process_id} exiting')
    

def create_tables_truncat(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `{DB_NAME}`.`{RROMO_TABLE}` (
                `promo_id` VARCHAR(10) PRIMARY KEY,
                `restaurant_id` VARCHAR(10),
                `total_coupons` INT,
                `left_coupons` INT
            );
        """)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `{DB_NAME}`.`{USER_COUPON_TABLE}` (
                `user_id` VARCHAR(10),
                `promo_id` VARCHAR(10),
                `process_id` INT,
                `time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, promo_id)
            );
        """)
        cursor.execute(f'truncate `{DB_NAME}`.`{USER_COUPON_TABLE}`;')
        conn.commit()
    
    logging.info('Tables created and truncated')


def main():
    # Create tables if they don't exist
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='example',
                           database=DB_NAME,
                           cursorclass=pymysql.cursors.DictCursor)
    create_tables_truncat(conn)

    # Populate some initial values in promotion table
    insert_record = f"""
        INSERT INTO {DB_NAME}.{RROMO_TABLE} (promo_id, restaurant_id, total_coupons, left_coupons)
        VALUES (%(promo_id)s, %(restaurant_id)s, %(total_coupons)s, %(left_coupons)s)
        ON DUPLICATE KEY UPDATE left_coupons = %(left_coupons)s
    """

    with conn.cursor() as cursor:
        cursor.execute(insert_record,
            {'promo_id': RPOMO_ID, 'restaurant_id': '67890', 'total_coupons': 200, 'left_coupons': 200})
        conn.commit()
    logging.info(f'Created **** 200 **** coupons in the database')

    # start a few worker processes
    logging.info('Starting processes...')
    processes = {}
    for i in range(NUM_PROCESSES):
        processes[i] = Process(target=consumer_process, args=(i,))
        processes[i].start()

    # Wait for the child processes to end
    logging.info('MAIN: wait for child processes to end')
    for p in processes.values():
        p.join()

    # Verify the sum of the left coupons and the number of added user coupons equals the total number
    #  of coupons in promotion table
    left_coupon = get_left_coupons(conn)
    num_user_coupons = get_user_coupon_num(conn)
    logging.info(f'Number of left coupons: {left_coupon}, and the number of user coupons: {num_user_coupons}')

    logging.info(f'MAIN: Exiting')


if __name__ == "__main__":
    main()