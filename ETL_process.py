import boto3
import json
import base64
import psycopg2
import configparser
import argparse
import sys
from datetime import datetime

class ETL_Process():
    """Class for performing ETL Process"""

    def __init__(self, endpoint_url, queue_name, wait_time, max_messages):
        config = configparser.ConfigParser()
        config.read('postgres.ini')
        self.__username = 'postgres'
        self.__password = 'postgres'
        self.__host = 'localhost'
        self.__database = 'postgres'
        self.__endpoint_url = endpoint_url
        self.__queue_name = queue_name
        self.__wait_time = wait_time
        self.__max_messages = max_messages
    
    def create_user_logins_table(self):
        try:
            postgres_conn = psycopg2.connect(
                host=self.__host,
                database=self.__database,
                user=self.__username,
                password=self.__password
            )
            print("Connected to PostgreSQL")

            cursor = postgres_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_logins (
                    user_id VARCHAR,
                    app_version VARCHAR,
                    device_type VARCHAR,
                    masked_ip VARCHAR,
                    locale VARCHAR,
                    masked_device_id VARCHAR,
                    create_date DATE
                )
            """)
            postgres_conn.commit()
            print("Table 'user_logins' created successfully")

        except Exception as e:
            print("Error:", e)

    def base64_encode(self, string_parameter, action="encode"):
        if action == "encode":
            ascii_string = string_parameter.encode('ascii')
            encoded_string = base64.b64encode(ascii_string).decode('utf-8')
            return encoded_string
        elif action == "decode":
            decoded_string = base64.b64decode(string_parameter).decode('utf-8')
            return decoded_string

    def get_messages(self):
        try:
            sqs_client = boto3.client("sqs", endpoint_url=self.__endpoint_url)
            response = sqs_client.receive_message(
                QueueUrl=self.__endpoint_url + '/' + self.__queue_name,
                MaxNumberOfMessages=self.__max_messages,
                WaitTimeSeconds=self.__wait_time
            )
            messages = response['Messages']
            return messages
        except Exception as exceptions:
            print("Error - Unable to receive messages:", exceptions)
            sys.exit()

    def transform_data(self, messages):
        message_list = []
        try:
            if len(messages) == 0:
                raise IndexError("Message list is empty")
        except IndexError as index_error:
            print("Error -", index_error)
            sys.exit()

        message_count = 0
        for message in messages:
            message_count += 1
            message_body = json.loads(message['Body'])
            try:
                ip = message_body['ip']
                device_id = message_body['device_id']
            except Exception as exception:
                print("Error - Message", message_count, "is invalid -", exception, "is not available in queue")
                continue

            base64_ip = self.base64_encode(ip)
            base64_device_id = self.base64_encode(device_id)

            message_body['ip'] = base64_ip
            message_body['device_id'] = base64_device_id

            message_list.append(message_body)

        return message_list

    def load_data_postgre(self, message_list):
        try:
            if len(message_list) == 0:
                raise TypeError("Message list is empty")
        except TypeError as type_error:
            print("Error -", type_error)
            sys.exit()

        try:
            postgres_conn = psycopg2.connect(
                host=self.__host,
                database=self.__database,
                user=self.__username,
                password=self.__password
            )
            print("Connected to PostgreSQL")
        except Exception as e:
            print("Error connecting to PostgreSQL:", e)
            sys.exit()

        cursor = postgres_conn.cursor()

        for message_json in message_list:
            message_json['locale'] = 'None' if message_json['locale'] == None else message_json['locale']
            message_json['create_date'] = datetime.now().strftime("%Y-%m-%d")
            values = list(message_json.values())
            cursor.execute("INSERT INTO user_logins ( \
                user_id, \
                app_version, \
                device_type, \
                masked_ip, \
                locale, \
                masked_device_id, \
                create_date \
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)", values)
            postgres_conn.commit()

        postgres_conn.close()
        print("Data loaded to PostgreSQL")


def main():
    parser = argparse.ArgumentParser(
        prog="Extract Transform Load - Process",
        description="Program extracts data from SQS queue - \
                       Transforms PIIs in the data - \
                       Loads the processed data into Postgres",
        epilog="Please raise an issue for code modifications"
    )
    parser.add_argument('-e', '--endpoint-url', required=True, help="Pass the endpoint URL here")
    parser.add_argument('-q', '--queue-name', required=True, help="Pass the queue URL here")
    parser.add_argument('-t', '--wait-time', type=int, default=10, help="Pass the wait time here")
    parser.add_argument('-m', '--max-messages', type=int, default=10, help="Pass the max messages to be pulled from SQS queue here")
    args = vars(parser.parse_args())
    endpoint_url = args['endpoint_url']
    queue_name = args['queue_name']
    wait_time = args['wait_time']
    max_messages = args['max_messages']
    etl_process_object = ETL_Process(endpoint_url, queue_name, wait_time, max_messages)
    etl_process_object.create_user_logins_table()
    print("Fetching messages from SQS Queue...")
    messages = etl_process_object.get_messages()
    print("Masking PIIs from the messages...")
    message_list = etl_process_object.transform_data(messages)
    print("Loading messages to Postgres...")
    etl_process_object.load_data_postgre(message_list)

if __name__ == "__main__":
    main()
