# Opteeq_Task_B

# Test Notebook

To run the test notebook create a python3 project in your prefered ide (eg. visual sudio code, pycharm etc.)

Then clone the repository by running 'git clone https://github.com/JonathanGriffiths94/Opteeq_Task_B.git' in your command line.

Then install the relevant packages from the requirements.txt file using 'pip3 install -r requirements.txt'

To test the Boto3 functions for reading and writing to s3 you will need to upload a test image to an s3 bucket and replace the values for the s3_bucket_name, key and region variables in the cell bellow. You can use the same bucket directory structure as shown here if you wish.

Next, if you have not already done so, run 'aws configure' in your command line to set up your aws security credentials, secret id, default region etc.

# Lambda Function 

Runtime: Python 3.7
Region: 'eu-west-1'
Memory allocation: 512mB
Timeout: 30 seconds

OpenCV and Numpy lambda layers found here https://github.com/keithrozario/Klayers. 

Layers used in testing (Layers are region specific):

OpenCV - arn:aws:lambda:eu-west-1:113088814899:layer:Klayers-python37-opencv-python-headless:13

Numpy - arn:aws:lambda:eu-west-1:113088814899:layer:Klayers-python37-numpy:11

Enviroment variables: 

out_bucket: opteeq-standardised-images

dynamodb_table_name: opteeq-dataset-table