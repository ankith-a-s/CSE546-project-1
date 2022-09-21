import boto3

ec2_client = boto3.client('ec2', region_name='us-east-1',
                          aws_secret_access_key="B8lwmuB6TU/Auv5VItwReN7YKfjPEiNGAL7tW8OT",
                          aws_access_key_id="AKIA2LNHGEXWNR5DVAWE")

AMI_ID = "ami-0bb1040fdb5a076bc"
ROLE_ARN = "arn:aws:iam::378107157540:instance-profile/sqs-s3-ec2-full-access"
SECURITY_GROUP = "sg-0dc6c0eb5cc4d9d27"
KEY_NAME = "new_app"
TAG_SPEC = [
    {
        "ResourceType": "instance",
        "Tags": [
            {
                "Key": "NAME",
                "Value": "App-Instance"
            }
        ]
    }
]


def create_instance():
    instances = ec2_client.run_instances(
        ImageId=AMI_ID,
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName=KEY_NAME,
        TagSpecifications=TAG_SPEC
    )
    print("Creating instance:", instances["Instances"][0]["InstanceId"])


def multiple_instance_create(num):
    print("Creating ", num, " instances")
    for _ in range(num):
        create_instance()


def start_instance(instance_id):
    print('Starting instance:', instance_id)
    response = ec2_client.start_instances(InstanceIds=[instance_id], DryRun=False)
    print(response)


def start_multiple_instances(instance_ids):
    print("Starting instances ", instance_ids)
    for i in instance_ids:
        start_instance(i)


def stop_instance(instance_id):
    print("Stopping instance: ", instance_id)
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    print(response)


def stop_multiple_instances(instance_ids):
    print("Stopping instances: ", instance_ids)
    for i in instance_ids:
        stop_instance(i)


def get_running_instances():
    instance_list = []
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running", "pending"],
        }
    ]).get("Reservations")

    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_list.append(instance_id)
    print("Running instances: ", instance_list)
    return instance_list


def get_stopped_instances():
    instance_list = []
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["stopped"],
        }
    ]).get("Reservations")

    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_list.append(instance_id)
    print("Stopped instances: ", instance_list)
    return instance_list


def get_all_instances():
    instance_list = []
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running", "stopped"],
        }
    ]).get("Reservations")

    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_list.append(instance_id)
    print("All instances: ", instance_list)
    return instance_list
