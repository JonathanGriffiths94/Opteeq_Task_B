# Opteeq_Task_B

# Test Notebook

To run the test notebook create a python3 project in your prefered ide (eg. visual sudio code, pycharm etc.)

Then clone the repository by running 'git clone https://github.com/JonathanGriffiths94/Opteeq_Task_B.git' in your command line.

Then install the relevant packages from the requirements.txt file using 'pip3 install -r requirements.txt'

To test the Boto3 functions for reading and writing to s3 you will need to upload a test image to an s3 bucket and replace the values for the s3_bucket_name, key and region variables in the cell bellow. You can use the same bucket directory structure as shown here if you wish.

Next, if you have not already done so, run 'aws configure' in your command line to set up your aws security credentials, secret id, default region etc.

# Lambda Function 