import React, { useRef, useState } from "react";
import "./App.css";

const maxFileSize = 5000;

function App() {
  const filesRef = useRef(null);
  const [fileError, setFileError] = useState({
    error: false,
    message: "",
  });

  function handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append("file", filesRef.current.files[0]);
    for (const value of formData.values()) {
      if (value.size && value.size < maxFileSize) {
        const fileType = value.name.split(".")[1].toLowerCase();
        if (fileType == "jpeg" || fileType == "png") {
          fetch("/upload_files", {
            method: "POST",
            body: formData,
          })
            .then((res) => console.log(res))
            .catch((err) => ("Error occured", err));
        } else {
          setFileError({
            ...fileError,
            error: true,
            message: "Please upload a file of type JPEG or PNG.",
          });
        }
      } else {
        setFileError({
          ...fileError,
          error: true,
          message: `Please upload a file of size less than ${maxFileSize} bytes.`,
        });
      }
    }
  }

  return (
    <div className="container">
      <div className="input-group">
        <label htmlFor="files">Select files</label>
        <input id="files" type="file" multiple ref={filesRef} />
      </div>
      <div>{fileError.error && fileError.message}</div>
      <button className="submit-btn" onClick={(e) => handleSubmit(e)}>
        Upload
      </button>
    </div>
  );
}

export default App;
