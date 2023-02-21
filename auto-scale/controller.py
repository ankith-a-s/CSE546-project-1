import instance_manager as ec2_util
import boto3
import time

sqs_client = boto3.client(
    'sqs',
    region_name= "us-east-1"
)


def get_sqs_url(client):
    sqs_queue = client.get_queue_url(QueueName="request-queue")
    return sqs_queue["QueueUrl"]


INPUT_QUEUE = get_sqs_url(sqs_client)

WEB_TIER = "i-032535b3abb75d937"
#APP_TIER = "i-082168043513b429a"


def auto_scale_instances():
    queue_length = int(
        sqs_client.get_queue_attributes(QueueUrl=INPUT_QUEUE, AttributeNames=['ApproximateNumberOfMessages']).get(
            "Attributes").get("ApproximateNumberOfMessages"))

    print("Request queue length:", queue_length)

    # band_dict = {0: 0, 20: 1, 100: 2, 500: 5, 1000: 19}

    running_instances = ec2_util.get_running_instances()
    stopped_instances = ec2_util.get_stopped_instances()
    running_instances.remove(WEB_TIER)
    # running_instances.remove(APP_TIER)

    if queue_length == 0:
        all_instances = ec2_util.get_running_instances()
        all_instances.remove(WEB_TIER)
        # all_instances.remove(APP_TIER)
        print("Queue is empty, shutting down all instances except 1 (downscaling)")
        ec2_util.stop_multiple_instances(all_instances)
        return

    elif 1 <= queue_length <= 5:
        if len(running_instances) == 0:
            if len(stopped_instances) >= 1:
                ec2_util.start_instance(stopped_instances[0])
            else:
                ec2_util.create_instance()

    elif 5 < queue_length <= 50:
        if len(running_instances) < 10:
            length_of_running = len(running_instances)
            length_of_stopped = len(stopped_instances)
            needed_instances = 10 - length_of_running
            if length_of_stopped >= needed_instances:
                ec2_util.start_multiple_instances(
                    stopped_instances[:needed_instances])
            else:
                ec2_util.start_multiple_instances(stopped_instances)
                for _ in range(needed_instances - length_of_stopped):
                    ec2_util.create_instance()

    else:
        if len(running_instances) < 18:
            length_of_running = len(running_instances)
            length_of_stopped = len(stopped_instances)
            needed_instances = 18 - length_of_running
            if length_of_stopped >= needed_instances:
                ec2_util.start_multiple_instances(
                    stopped_instances[:needed_instances])
            else:
                ec2_util.start_multiple_instances(stopped_instances)
                for _ in range(needed_instances - length_of_stopped):
                    ec2_util.create_instance()


print("Starting Auto Scaling")
while(True):
    auto_scale_instances()
    time.sleep(30)
exit(0)
