require("dotenv").config();
const S3 = require("aws-sdk/clients/s3");
const fs = require("fs");
const util = require("util");

const bucketName = "inputimagernaik99";
const region = "us-east-1";

const s3 = new S3({
  region,
});

function uploadImageToS3(file) {
  const fileStream = fs.createReadStream(file.path);

  const uploadParams = {
    Bucket: bucketName,
    Body: fileStream,
    Key: file.originalname,
  };

  return s3.upload(uploadParams).promise();
}

module.exports = {
  uploadImageToS3,
};
