SQS Queue ETL Process
This project demonstrates an Extract-Transform-Load (ETL) process using AWS Simple Queue Service (SQS), data transformation, and loading the transformed data into a PostgreSQL database. It involves extracting messages from an SQS queue, masking sensitive data, and then storing the processed data into a PostgreSQL database.

Prerequisites
Docker: Ensure you have Docker installed on your system.
Postgres
Aws-cli
Aws

Getting Started
Clone the repository:

git clone <repository-url>
cd sqsqueue

To run this project follow the steps below:
1) Install the dependencies:

Command to run: pip install -r dependencies.txt

2) Configure the AWS credentials:
Command: ./aws_configure.sh 

or 

bash aws_configure.sh

3) Build and Run Containers:

Run the following command to start/stop the required Docker containers:
(Please make sure Docker Desktop is Up and Running before executing these lines.)
start:
    docker-compose up -d

stop:
    docker-compose down --remove-orphans


4) Run the ETL Process:

Run the ETL process Python script using the following command:

python ETL_process.py --endpoint-url http://localhost:4566 --queue-name login-queue --max-messages 25

5) Verify Data in PostgreSQL:

You can connect to the PostgreSQL database using a tool of your choice (e.g., psql) and check if the processed data has been loaded into the database.
Use command: 
psql -h localhost -p 5432 -U postgres -d postgres -W

and then type: SELECT * FROM user_logins;

Troubleshooting
If you encounter issues related to the connection or data processing, refer to the error messages in the console output for guidance.

Verify that the PostgreSQL container is running and listening on the correct port.

Use the following postgres credentials:
username="postgres"
password="postgres"
host="localhost"
database="postgres"

License
This project is licensed under the MIT License - see the LICENSE file for details.

Feel free to modify this template to fit the specifics of your project. Make sure to replace placeholders with actual values and customize the instructions and descriptions as needed.
