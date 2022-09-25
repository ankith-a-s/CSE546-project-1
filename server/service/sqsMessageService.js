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

const awsAccountId = 524883170635;
const sqsInputQueue = "Request-Queue";
const sqsOutputQueue = "Response-Queue";

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
      res.status(400).send({
        message: "Some error occured",
        data,
      });
    } else {
      if (data.Messages) {
        const imageData = JSON.parse(data.Messages[0].Body);
        if (Object.keys(imageData)[0] == imageName) {
          const deleteParams = {
            QueueUrl: `https://sqs.us-east-1.amazonaws.com/${awsAccountId}/${sqsOutputQueue}`,
            ReceiptHandle: data.Messages[0].ReceiptHandle,
          };
          sqs.deleteMessage(deleteParams, (err, data) => {
            if (err) {
              console.log(err, err.stack);
              res.status(400).send({
                message: "Some error occured",
                data,
              });
            } else {
              res.status(200).send({
                message: imageData[imageName],
              });
              console.log("reaching this point");
              logger.info(`Served request with image name ${imageName}`);
            }
          });
        } else {
          return receiveMessageFromSqs(imageName, res);
        }
      } else {
        return receiveMessageFromSqs(imageName, res);
      }
    }
  });
};

module.exports = {
  sendMessageToSqs,
  receiveMessageFromSqs,
};
