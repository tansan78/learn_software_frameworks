'''
This is to simulate the database operations for the coupon system.
- a promotion allows certain amount of coupons
- every user can sign up at most once and get one coupon

You need to implement the following functions:
- create tables, without exception even if the tables already exist: create_tables_truncate()
- create promotion with a specified number of allowed coupons: create_promotion()
- sign up a promotion (substracting number of left coupons from promotion and adding records for users): user_sign_up_promo()
- get the number of left coupons for a promotion: get_left_coupons()
- get all the available coupons for a user: get_user_coupon_num()

Please handle possible race conditions!
'''
import logging
import time
import random 

from multiprocessing import Process

import pymysql


# The number of web server processes
NUM_PROCESSES = 3

DB_NAME = 'testdb'
RROMO_TABLE = 'promotions'
USER_COUPON_TABLE = 'user_coupons'
RPOMO_ID = '123456'

logging.basicConfig(level=logging.INFO)


def web_server_process(process_id):
    '''
    This emulates the web server processes. There will be multiple server processes; each process
    will independently decrement the left coupons in promotion and create user coupon record in database.

    Please do not reference any global variables except constants.
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

        user_sign_up_promo(conn, process_id, rand_user)
        
        sleep_time = random.uniform(0.1, 1.0)
        time.sleep(sleep_time)
    
    logging.info(f'Process {process_id} exiting')


def main():
    # Create tables if they don't exist
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='example',
                           database=DB_NAME,
                           cursorclass=pymysql.cursors.DictCursor)
    create_tables_truncate(conn)

    # Populate some initial values in promotion table
    create_promotion(conn, total_allowed_coupon=200)

    # start a few worker processes
    logging.info('Starting processes...')
    processes = {}
    for i in range(NUM_PROCESSES):
        processes[i] = Process(target=web_server_process, args=(i,))
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
    if left_coupon + num_user_coupons != 200:
        logging.error(f'Data inconsistency detected: the sum of left coupons and the used coupons is not 200')

    logging.info(f'MAIN: Exiting')


def user_sign_up_promo(conn, process_id: int, user_id: str, promo_id: str=RPOMO_ID):
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
        cursor.execute(decrement_coupons, {'promo_id': RPOMO_ID, 'user_id': user_id})
        try:
            cursor.execute(add_user_coupon, {'promo_id': RPOMO_ID, 'user_id': user_id})
            conn.commit()
        except pymysql.err.IntegrityError as e:
            conn.rollback()
            logging.warning(f'Process {process_id}: Duplicated user found: {user_id}')


def create_tables_truncate(conn):
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


def create_promotion(conn, promo_id=RPOMO_ID, total_allowed_coupon=200):
    insert_record = f"""
        INSERT INTO {DB_NAME}.{RROMO_TABLE} (promo_id, restaurant_id, total_coupons, left_coupons)
        VALUES (%(promo_id)s, %(restaurant_id)s, %(total_coupons)s, %(left_coupons)s)
        ON DUPLICATE KEY UPDATE left_coupons = %(left_coupons)s
    """

    with conn.cursor() as cursor:
        cursor.execute(insert_record,
            {'promo_id': promo_id, 'restaurant_id': '67890',
             'total_coupons': total_allowed_coupon, 'left_coupons': total_allowed_coupon})
        conn.commit()
    logging.info(f'Created **** 200 **** coupons in the database')


def get_left_coupons(conn, promo_id=RPOMO_ID):
    with conn.cursor() as cursor:
        fetch_left_coupons = f"""
            SELECT left_coupons from `{DB_NAME}`.`{RROMO_TABLE}`
            WHERE promo_id = %(promo_id)s;
        """
        cursor.execute(fetch_left_coupons, {'promo_id': promo_id})
        left_coupon = cursor.fetchone()['left_coupons']
    
    return left_coupon


def get_user_coupon_num(conn, promo_id=RPOMO_ID):
    with conn.cursor() as cursor:
        get_user_record = f"""
            SELECT count(*) as cnt from `{DB_NAME}`.`{USER_COUPON_TABLE}`
            WHERE promo_id = %(promo_id)s;
        """

        cursor.execute(get_user_record, {'promo_id': promo_id})
        num_user_coupons = cursor.fetchone()['cnt']
    
    return num_user_coupons


if __name__ == "__main__":
    main()