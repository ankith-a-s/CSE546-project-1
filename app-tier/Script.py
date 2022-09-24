from fileinput import filename
from botocore.exceptions import ClientError
from urllib import response
import boto3
import json
import os
import subprocess

def get_queue_url(queue_name):
    sqs_client = boto3.client("sqs", region_name = "us-east-1")
    name = queue_name
    queue_name = sqs_client.get_queue_url(
        QueueName = name
    )
    return queue_name["QueueUrl"]


def write_message(queue_url, message_body):
    sqs_client = boto3.client("sqs", region_name = "us-east-1")
    # name = "Request-Queue"
    # message = {"Image_Name": "Test_0.jpeg"}
    message = message_body
    response = sqs_client.send_message(
        QueueUrl = queue_url,
        MessageBody = json.dumps(message)
    )
   
    return response['ResponseMetadata']["HTTPStatusCode"]

def read_message(queue_url):
    response = []
    sqs_client = boto3.client("sqs", region_name = "us-east-1")
    response = sqs_client.receive_message(
        QueueUrl = queue_url,
        MaxNumberOfMessages =1, 
        WaitTimeSeconds=10,
    )
    if len(response.get("Messages", []))>0:
        for message in response.get("Messages", []):
            message_body = message["Body"]
        message_body = json.loads(message_body)
        return message_body["Image_Name"], message['ReceiptHandle']
    else:
        return None, None

def delete_message(queue_url,receipt_handle):
    sqs_client = boto3.client("sqs", region_name = "us-east-1")
    response = sqs_client.delete_message(
        QueueUrl = queue_url,
        ReceiptHandle=receipt_handle,
    )
    return response["ResponseMetadata"]["HTTPStatusCode"]

def run_classification_engine():
    dir_path = '/home/ubuntu/images/'
    for path in os.listdir(dir_path):
        path = '/home/ubuntu/images/' + str(path)
        filename = path.rsplit(".",1)[0]
        filename = filename.rsplit("/")[4]
        filename = '/home/ubuntu/result/'+ str(filename) + '.txt'
        subprocess.run(['touch', filename])
        output_file = open(filename, "w")
        subprocess.run(('python3', './image_classification.py', path ), stdout=output_file)

def downoad_images(s3_bucket_name, image_name):
    session = boto3.session.Session()
    s3_resource = session.resource("s3")
    file_name = '/home/ubuntu/images/' + image_name
    s3_resource.meta.client.download_file(s3_bucket_name,image_name,file_name)


def delete_image(image_name):
    file_path = "/home/ubuntu/images/" + image_name
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("The file does not exist")
    return True

def write_classification_msg(image_name, queue_url):
    path = '/home/ubuntu/images/' + str(image_name)
    file_name = path.rsplit(".",1)[0]
    file_name = file_name.rsplit("/")[4]
    file_name = '/home/ubuntu/result/'+ str(file_name) + '.txt'
    with open (file_name,'r') as f:
        lines = f.readline()
    lines = lines.split("\n")
    message_body = lines[0].split(",")[1]
    sqs_message = {image_name : message_body}
    status_code = write_message(queue_url, sqs_message )
    return status_code 

def write_to_bucket(s3_bucket_name, image_name): ##function to upload classification result to output S3 bucket
    path = '/home/ubuntu/images/' + str(image_name)
    file_name = path.rsplit(".",1)[0]
    file_name = file_name.rsplit("/")[4]
    result_file = '/home/ubuntu/result/'+ str(file_name) + '.txt'
    with open (result_file, 'r') as f:
        lines = f.readline()
    lines = lines.split("\n")
    message_body = file_name + "," + lines[0].split(",")[1]
    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket = s3_bucket_name, Body=message_body, Key = file_name)

if __name__=="__main__":
    request_queue = get_queue_url("Request-Queue")
    response_queue = get_queue_url("Response-Queue")
    image_name, reciept_handle = read_message(request_queue)
    input_bucket = "inputimageabhinav0907"
    output_bucket = "outputresultabhinav0907"
    if image_name!=None and reciept_handle!=None : 
        downoad_images(input_bucket, image_name)
        run_classification_engine()
        write_classification_msg(image_name, response_queue)
        write_to_bucket(output_bucket, image_name)
        delete_message(request_queue, reciept_handle)
        delete_image(image_name)
        exit(0)
    else:
        exit(1)
