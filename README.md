# CSE546

<p>To run the project, create an EC2 instance for the web tier with a public IP.
Create the following AWS services in the us-east-1 region only and configure aws cli on the wev tier.
Pull the code into a location and start the node server with the following command:</p>

**pm2 start index.js**

Create a system service for the web tier to start the controller script.

Create 2 SQS Queues with the names: 1. Request-Queue 2. Response- Queue

Create 2 S3 buckets with the following names and make the bucket objects public while creating them:
1. <br>
2. <br>
<hr>

Run the workload generator and wait for the response from the web server.