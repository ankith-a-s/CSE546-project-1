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

const app = express();
app.use(express.json());
const upload = multer({ dest: __dirname + "uploads/" });

app.post("/upload_files", upload.single("myfile"), async (req, res) => {
  const s3Result = await uploadImageToS3(req.file);
  await unlinkFile(req.file.path);
  if (s3Result) {
    const sqsResult = await sendMessageToSqs(req.file.originalname, res);
    if (sqsResult != undefined) {
      await receiveMessageFromSqs(req.file.originalname, res);
    }
  }
});

app.use(express.static("./public"));

const hostname = "0.0.0.0";
app.listen(PORT, hostname, () => {
  console.log(`Server listening on ${PORT}`);
});
