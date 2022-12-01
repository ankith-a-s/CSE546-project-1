require("dotenv").config();
const express = require("express");
const multer = require("multer");
const fs = require("fs");
const util = require("util");
const unlinkFile = util.promisify(fs.unlink);

const {
  sendMessageToSqs,
  receiveMessageFromSqs,
} = require("./service/sqsMessageService.js");
const { uploadImageToS3 } = require("./service/s3UploadService.js");

const PORT = process.env.PORT || 3001;

const timeoutLimit = 100000000000;

const app = express();
app.use(express.json());
const upload = multer({ dest: __dirname + "uploads/" });

const asyncCallWithTimeout = async (asyncPromise, timeLimit) => {
    let timeoutHandle;

    const timeoutPromise = new Promise((_resolve, reject) => {
        timeoutHandle = setTimeout(
            () => reject(new Error('Async call timeout limit reached')),
            timeLimit
        );
    });

    return Promise.race([asyncPromise, timeoutPromise]).then(result => {
        clearTimeout(timeoutHandle);
        return result;
    })
}

app.post("/upload_files", upload.single("myfile"), uploadFiles);

const uploadFiles = async (req, res) => {
  const s3Result = await asyncCallWithTimeout(uploadImageToS3(req.file), timeoutLimit);
  await asyncCallWithTimeout(unlinkFile(req.file.path), timeoutLimit);
  if (s3Result) {
    const sqsResult = await asyncCallWithTimeout(sendMessageToSqs(req.file.originalname, res), timeoutLimit);
    if (sqsResult != undefined) {
      await asyncCallWithTimeout(receiveMessageFromSqs(req.file.originalname, res), timeoutLimit);
    }
  }
}

app.use(express.static("./public"));

const hostname = "0.0.0.0";
app.listen(PORT, hostname, () => {
  console.log(`Server listening on ${PORT}`);
});
