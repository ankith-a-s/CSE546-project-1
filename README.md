# CSE546

<p>To run the project, create an EC2 instance for the web tier with a public IP.
Create the following AWS services in the us-east-1 region only and configure aws cli on the web tier.
Start the node server with the follwoing command.</p>

**pm2 start index.js**


Create 2 SQS Queues with the names: <br>
1. Request-Queue <br>
1. Response- Queue

Create 2 S3 buckets with the following names and make the bucket objects public while creating them:
1. inputimageabhinav0907<br>
2. outputresultabhinav0907<br>
<hr>

Run the workload generator and wait for the response from the web server.