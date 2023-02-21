import boto3

ec2_client = boto3.client('ec2', region_name='us-east-1')

AMI_ID = "ami-04c3241d59e04ca70"
ROLE_ARN = "arn:aws:iam::692988731852:role/aws-full-access"
KEY_NAME = "CC Project 1"
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
    instance_num=len(get_running_instances())+1
    TAG_SPEC = [
        {
            "ResourceType": "instance",
            "Tags": [
                {
                    "Key": "NAME",
                    "Value": "App-Instance-"+str(instance_num)
                }
            ]
        }
    ]
    instances = ec2_client.run_instances(
        ImageId=AMI_ID,
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName=KEY_NAME,
        # SubnetId="subnet-0363c5f153dd2e1fb",
        # SecurityGroupIds=["sg-023a5e1617e20d3cd"],
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
