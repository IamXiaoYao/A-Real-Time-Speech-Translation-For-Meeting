import React, { useState } from 'react'
import { Mic, StopCircle, Upload, RefreshCw, FileText } from 'lucide-react'

function App() {
  const [text, setText] = useState('')
  const [isRecording, setIsRecording] = useState(false)

  const handleRecord = () => {
    setIsRecording(!isRecording)
  }

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
            <p className="subtitle">Transform your speech into text instantly</p>
            <p className="subtitle">
              By <strong>Xiao Yao</strong>
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
              value={text}
              readOnly
              placeholder="Your speech will appear here..."
              className="textarea"
            />

            {/* Controls */}
            <div className="controls">
              <div className="controls-left">
                <button
                  onClick={handleRecord}
                  className={`btn btn-primary ${isRecording ? 'recording' : ''}`}
                >
                  {isRecording ? <StopCircle /> : <Mic />}
                  {isRecording ? 'Stop' : 'Start Recording'}
                </button>

                <button className="btn btn-icon">
                  <RefreshCw />
                </button>
              </div>

              <div className="controls-right">
                <button className="btn btn-icon">
                  <FileText />
                  <span>Copy</span>
                </button>
                <button className="btn btn-icon">
                  <Upload />
                  <span>Upload</span>
                </button>
              </div>
            </div>
          </div>

          {/* Features */}
          {/*           <div className="features">
            <div className="feature-card">
              <h3 className="feature-title">Real-time Transcription</h3>
              <p className="feature-description">
                Instantly convert your speech to text with high accuracy
              </p>
            </div>
            <div className="feature-card">
              <h3 className="feature-title">Multiple Languages</h3>
              <p className="feature-description">Support for various languages and accents</p>
            </div>
            <div className="feature-card">
              <h3 className="feature-title">Smart Punctuation</h3>
              <p className="feature-description">Automatic punctuation and formatting</p>
            </div>
          </div> */}
        </div>
      </div>
    </div>
  )
}

export default App
