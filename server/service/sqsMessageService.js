const AWS = require("aws-sdk");
const bunyan = require("bunyan");

const logger = bunyan.createLogger({
  name: "classificationResponseLogs",
  streams: [
    {
      level: "debug",
      stream: process.stdout,
    },
    {
      level: "info",
      path: "./logs.txt",
    },
  ],
});

//Configure region
AWS.config.update({ region: "us-east-1" });
//Create SQS client
const sqs = new AWS.SQS({ apiVersion: "2012-11-05" });

const awsAccountId = 692988731852;
const sqsInputQueue = "request-queue";
const sqsOutputQueue = "response-queue";

const sendMessageToSqs = (Image_Name, res) => {
  const params = {
    MessageBody: JSON.stringify({
      Image_Name,
    }),
    QueueUrl: `https://sqs.us-east-1.amazonaws.com/${awsAccountId}/${sqsInputQueue}`,
  };

  return sqs.sendMessage(params, (err, data) => {
    if (err) {
      console.log("sendMessage");
      res.status(400).send({
        message: "Some error occured",
        data,
      });
    }
  });
};

const receiveMessageFromSqs = (imageName, res) => {
  const params = {
    QueueUrl: `https://sqs.us-east-1.amazonaws.com/${awsAccountId}/${sqsOutputQueue}`,
    VisibilityTimeout: 0,
    WaitTimeSeconds: 0,
  };

  sqs.receiveMessage(params, (err, data) => {
    if (err) {
      console.log("receiveMessage");
      logger.debug(`Some error occured in receiving messages, ${data}`);
    } else {
      if (data.Messages) {
        for (let i = 0; i < data.Messages.length; i++) {
          const imageData = JSON.parse(data.Messages[i].Body);
          const deleteParams = {
            QueueUrl: `https://sqs.us-east-1.amazonaws.com/${awsAccountId}/${sqsOutputQueue}`,
            ReceiptHandle: data.Messages[i].ReceiptHandle,
          };
          sqs.deleteMessage(deleteParams, (err, data) => {
            if (err) {
              console.log(err, err.stack);
              logger.debug(`Some error occured in receiving messages, ${err}`);
            } else {
              console.log("reaching this point");
              logger.info(`Served request with image file name ===> ${Object.keys(imageData)[0]}, prediction ===> ${Object.values(imageData)[0]}`);
            }
          });
        }
      } 
    }
  });
};

module.exports = {
  sendMessageToSqs,
  receiveMessageFromSqs,
};
