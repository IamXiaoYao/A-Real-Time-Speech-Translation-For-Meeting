import { Clipboard, Mic, StopCircle, Trash2, Upload } from "lucide-react";
import React, { useEffect, useState } from "react";

function App() {
  const [text, setText] = useState(""); // For transcription text
  const [isRecording, setIsRecording] = useState(false); // Recording state
  const [transcription, setTranscription] = useState(""); // For real-time updates
  const [error, setError] = useState(""); // For error handling
  const [selectedLanguage, setSelectedLanguage] = useState("en"); // Default to English
  const [copied, setCopied] = useState(false); // Track copy status

  const languages = [
    { code: "en", name: "English" },
    { code: "fra", name: "French" },
    { code: "zh", name: "Chinese" },
    { code: "spa", name: "Spanish" },
    { code: "de", name: "German" },
    { code: "jp", name: "Japanese" },
  ];

  useEffect(() => {
    const handlePythonResponse = (response) => {
      if (response.error) {
        setError(response.error);
      } else if (response.result) {
        setTranscription((prev) => {
          return prev.includes(response.result) ? prev : `${prev}\n${response.result}`;
        });
      }
    };

    if (window.pythonAPI) {
      window.pythonAPI.onResponse(handlePythonResponse);
    } else {
      console.error("pythonAPI is not available");
    }

    return () => {
      if (window.pythonAPI) {
        window.pythonAPI.onResponse(() => { });
      }
    };
  }, []);

  const handleRecord = () => {
    setError("");
    setSelectedLanguage("en");
    if (isRecording) {
      setIsRecording(false);
      window.pythonAPI.call("stop_recording");
    } else {
      setIsRecording(true);
      window.pythonAPI.call("record_audio");
    }
  };


  const handleUpload = async () => {
    setError("");
    setSelectedLanguage("en");
    try {
      const [fileHandle] = await window.showOpenFilePicker({
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

      if (!fileHandle) return;

      const file = await fileHandle.getFile();
      const reader = new FileReader();

      reader.onload = async () => {
        const base64Audio = reader.result.split(",")[1];
        window.pythonAPI.call("transcribe_base64", [base64Audio, file.type]);
      };

      reader.readAsDataURL(file);
    } catch (err) {
      console.error("Error uploading file:", err);
      setError("Failed to upload the file.");
    }
  };

  const handleClearText = () => {
    setTranscription("");
  };

  const handleCopyText = () => {
    navigator.clipboard.writeText(transcription).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // Reset "Copied!" after 2 seconds
    });
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
              Transform your meeting speech into text instantly
            </p>
          </header>

          {/* Language Selection - Moved to Top */}
          <div className="language-selector">
            <label>Output Language: </label>
            <select value={selectedLanguage} onChange={(e) => setSelectedLanguage(e.target.value)}>
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

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

            {/* Scrollable Transcription Box */}
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
                <button onClick={handleRecord} className={`btn btn-primary ${isRecording ? "recording" : ""}`}>
                  {isRecording ? <StopCircle /> : <Mic />}
                  {isRecording ? "Stop" : "Start Recording"}
                </button>
                <button onClick={handleClearText} className="btn btn-icon">
                  <Trash2 />
                  <span>Clear All</span>
                </button>
                <button onClick={handleCopyText} className="btn btn-secondary">
                  <Clipboard />
                  <span>{copied ? "Copied!" : "Copy All"}</span>
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
