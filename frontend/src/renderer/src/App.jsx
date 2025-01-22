import React, { useState, useEffect } from "react";
import { Mic, StopCircle, Upload, RefreshCw, FileText } from "lucide-react";

function App() {
  const [text, setText] = useState(""); // For transcription text
  const [isRecording, setIsRecording] = useState(false); // Recording state
  const [transcription, setTranscription] = useState(""); // For real-time updates
  const [error, setError] = useState(""); // For error handling

  useEffect(() => {
    // Set up a listener for Python's responses
    const handlePythonResponse = (response) => {
      if (response.error) {
        setError(response.error);
      } else if (response.result) {
        // Append the new transcription to the existing text
        setTranscription((prev) => `${prev}\n${response.result}`);
      }
    };

    // Add the response listener
    if (window.pythonAPI) {
      window.pythonAPI.onResponse(handlePythonResponse);
    } else {
      console.error("pythonAPI is not available");
    }

    // Cleanup listener on component unmount
    return () => {
      if (window.pythonAPI) {
        window.pythonAPI.onResponse(() => {}); // Clear the listener
      }
    };
  }, []);

  const handleRecord = () => {
    setError("");
    setTranscription("");
    if (isRecording) {
      // Stop recording
      setIsRecording(false);
      window.pythonAPI.call("stop_recording");
    } else {
      // Start recording
      setIsRecording(true);
      setText("");
      window.pythonAPI.call("record_audio");
    }
  };

  const handleUpload = async () => {
    setError("");
    try {
      const file = await window.showOpenFilePicker({
        types: [
          {
            description: "Audio Files",
            accept: {
              "audio/*": [".wav", ".mp3", ".m4a", ".ogg"],
            },
          },
        ],
        multiple: false,
      });

      if (file.length > 0) {
        const filePath = await file[0].getFile();
        window.pythonAPI.call("transcribe", [filePath.path]);
      }
    } catch (err) {
      console.error("Error uploading file:", err);
      setError("Failed to upload the file.");
    }
  };

  return (
    <div className="app">
      <div className="container">
        <div className="content">
          {/* Header */}
          <header className="header">
            <div className="logo">
              <Mic />
            </div>
            <h1 className="title">VoiceFlow</h1>
            <p className="subtitle">
              Transform your speech into text instantly
            </p>
          </header>

          {/* Main Content */}
          <div className="main-content">
            <div className="recording-status">
              {isRecording ? (
                <div className="recording-indicator">
                  <span className="pulse"></span>
                  <span>Recording...</span>
                </div>
              ) : (
                <span>Click the microphone to start recording</span>
              )}
            </div>

            <textarea
              value={transcription || "Your transcription will appear here..."}
              readOnly
              className="textarea"
            />

            {/* Error Message */}
            {error && <p className="error-message">{error}</p>}

            {/* Controls */}
            <div className="controls">
              <div className="controls-left">
                <button
                  onClick={handleRecord}
                  className={`btn btn-primary ${isRecording ? "recording" : ""}`}
                >
                  {isRecording ? <StopCircle /> : <Mic />}
                  {isRecording ? "Stop" : "Start Recording"}
                </button>
              </div>

              <div className="controls-right">
                <button onClick={handleUpload} className="btn btn-icon">
                  <Upload />
                  <span>Upload</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
