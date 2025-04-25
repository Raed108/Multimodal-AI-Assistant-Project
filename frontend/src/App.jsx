import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { ReactMediaRecorder } from "react-media-recorder";
import ConstraintInput from "./components/ConstraintInput";
import ResponseDisplay from "./components/ResponseDisplay";
import KnowledgeGraphDisplay from "./components/KnowledgeGraphDisplay";
import WaveSurfer from "wavesurfer.js";
import { Moon, Sun } from "lucide-react";

export default function App() {
  const [question, setQuestion] = useState("");
  const [logicalGroups, setLogicalGroups] = useState([]);
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [image, setImage] = useState(null);
  const [mode, setMode] = useState("text1");
  const [maleSpeaker, setMaleSpeaker] = useState(true);
  const [audioUrl, setAudioUrl] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const waveformRef = useRef(null);
  const [waveform, setWaveform] = useState(null);
  const [isWaveformReady, setIsWaveformReady] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [dots, setDots] = useState("");
  const [loadingSeconds, setLoadingSeconds] = useState(0);
  const [responseTime, setResponseTime] = useState(0);
  const [iterationCount, setIterationCount] = useState(0);
  const [imageGenerationTime, setImageGenerationTime] = useState(0);
  const [responseA, setResponseA] = useState("");
  const [responseB, setResponseB] = useState("");
  const [analysisBofA, setAnalysisBofA] = useState("");
  const [analysisAofB, setAnalysisAofB] = useState("");

  // Handle loading seconds and dots
  useEffect(() => {
    if (!isLoading) {
      setLoadingSeconds(0);
      setDots("");
      return;
    }
    const secondsInterval = setInterval(() => {
      setLoadingSeconds((prev) => prev + 1);
    }, 1000);
    const dotsInterval = setInterval(() => {
      setDots((prev) => (prev.length < 3 ? prev + "." : ""));
    }, 500);
    return () => {
      clearInterval(secondsInterval);
      clearInterval(dotsInterval);
    };
  }, [isLoading]);

  // Reset all state when mode changes
  useEffect(() => {
    // Reset input and output states
    setQuestion("");
    setLogicalGroups([]);
    setResponse("");
    setResponseA("");
    setResponseB("");
    setAnalysisBofA("");
    setAnalysisAofB("");
    setImage(null);
    setAudioUrl(null);
    setRecordingTime(0);
    setIsWaveformReady(false);
    setIsPlaying(false);
    setResponseTime(0);
    setImageGenerationTime(0);
    setIterationCount(0);

    // Reset waveform if it exists
    if (waveform) {
      waveform.stop();
      waveform.empty();
    }
  }, [mode, waveform]);

  useEffect(() => {
    let timer;
    if (isLoading) return;
    if (recordingTime > 0) {
      timer = setInterval(() => setRecordingTime((prev) => prev + 1), 1000);
    }
    return () => clearInterval(timer);
  }, [recordingTime, isLoading]);

  useEffect(() => {
    if (waveformRef.current && !waveform) {
      const ws = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: "#34d399",
        progressColor: "#10b981",
        height: 50,
        barWidth: 2,
        cursorWidth: 1,
        cursorColor: "#357abd",
        responsive: true,
        interact: true,
      });
      ws.on("ready", () => {
        console.log("Waveform is ready for playback");
        setIsWaveformReady(true);
      });
      ws.on("play", () => {
        console.log("Waveform started playing");
        setIsPlaying(true);
      });
      ws.on("pause", () => {
        console.log("Waveform paused");
        setIsPlaying(false);
      });
      ws.on("finish", () => {
        console.log("Waveform playback finished");
        ws.stop();
        setIsPlaying(false);
        setIsWaveformReady(true);
      });
      ws.on("error", (err) => {
        console.error("WaveSurfer error:", err);
        setIsWaveformReady(false);
      });
      setWaveform(ws);
    }
  }, [waveform]);

  const handleGenerateResponse1 = async () => {
    setIsLoading(true);
    setResponse("");
    setAudioUrl(null);
    const startTime = performance.now();
    try {
      const res = await axios.post("http://localhost:8000/generate_response/", {
        question,
        logicalGroups,
      });
      console.log("API Response:", res.data);
      setResponse(res.data.response);
      setResponseTime(Math.round((performance.now() - startTime) / 1000));
      setIterationCount(res.data.iterationCount);
    } catch (error) {
      console.error("Error generating response:", error);
      setResponse("Error generating response. Please try again.");
      setResponseTime(Math.round((performance.now() - startTime) / 1000));
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateResponse2 = async () => {
    setIsLoading(true);
    setResponseA("");
    setResponseB("");
    setAnalysisBofA("");
    setAnalysisAofB("");
    setAudioUrl(null);
    const startTime = performance.now();
    try {
      const res = await axios.post("http://localhost:8000/generate_valid_response/", {
        question,
        logicalGroups,
      });
      console.log("API Response:", res.data);
      setResponseA(res.data.response_A);
      setResponseB(res.data.response_B);
      setAnalysisBofA(res.data.analysis_B_of_A);
      setAnalysisAofB(res.data.analysis_A_of_B);
      setResponseTime(Math.round((performance.now() - startTime) / 1000));
    } catch (error) {
      console.error("Error generating response:", error);
      setResponseA("Error generating response. Please try again.");
      setResponseB("Error generating response. Please try again.");
      setResponseTime(Math.round((performance.now() - startTime) / 1000));
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateImage = async () => {
    setIsLoading(true);
    setImage(null);
    const startTime = performance.now();
    try {
      const response = await axios.post("http://localhost:8000/generate_image/", {
        logicalGroups,
      });
      console.log("API Response:", response.data);
      setImage(response.data.image);
      setImageGenerationTime(Math.round((performance.now() - startTime) / 1000));
    } catch (error) {
      console.error("Error generating image:", error);
      setImageGenerationTime(Math.round((performance.now() - startTime) / 1000));
    } finally {
      setIsLoading(false);
    }
  };

  const handleTranscription = async (blob) => {
    if (!blob) {
      console.error("No blob available for transcription");
      return;
    }
    const formData = new FormData();
    formData.append("file", blob, "recorded_audio.webm");
    try {
      const res = await axios.post("http://localhost:8000/transcribe/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setQuestion(res.data.transcription);
      if (waveform) {
        setIsWaveformReady(false);
        waveform.loadBlob(blob);
      }
    } catch (error) {
      console.error("Transcription failed:", error.response?.data || error.message);
    }
  };

  const handleSpeakResponse = async (text, onAudioStart) => {
    try {
      const res = await axios.post("http://localhost:8000/api/text-to-speech/", {
        text,
        maleSpeaker,
      });
      const audioBase64 = res.data.audio;
      if (!audioBase64) throw new Error("No audio data returned");
      const audioBlob = new Blob([Uint8Array.from(atob(audioBase64), (c) => c.charCodeAt(0))], { type: "audio/wav" });
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);
      const audio = new Audio(url);
      audio.onplay = () => {
        if (onAudioStart) onAudioStart();
      };
      return { audio, url };
    } catch (error) {
      console.error("TTS failed:", error.response?.data || error.message);
      if (onAudioStart) onAudioStart();
      throw error;
    }
  };

  const handleDownloadImage = () => {
    if (!image) return;
    const link = document.createElement("a");
    link.href = `data:image/png;base64,${image}`;
    link.download = "generated_image.png";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const toggleDarkMode = () => {
    setDarkMode((prev) => !prev);
  };

  const containerStyle = {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh",
    padding: "1rem",
    backgroundColor: darkMode ? "#1a202c" : "#47556a",
    transition: "background-color 0.3s",
  };

  const cardStyle = {
    maxWidth: "32rem",
    width: "100%",
    padding: "1.5rem",
    backgroundColor: darkMode ? "#2d3748" : "#e1e5eb",
    borderRadius: "0.5rem",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    transition: "background-color 0.3s",
  };

  const textStyle = {
    color: darkMode ? "#e2e8f0" : "#1a1a1a",
  };

  const inputStyle = {
    width: "97%",
    padding: "0.5rem",
    border: `1px solid ${darkMode ? "#4a5568" : "#e2e8f0"}`,
    borderRadius: "0.25rem",
    marginBottom: "1rem",
    backgroundColor: darkMode ? "#4a5568" : "#f9fafb",
    color: darkMode ? "#e2e8f0" : "#1a1a1a",
    maxWidth: "100%",
  };

  const selectStyle = {
    width: "100%",
    padding: "0.5rem",
    border: `1px solid ${darkMode ? "#4a5568" : "#e2e8f0"}`,
    borderRadius: "0.25rem",
    backgroundColor: darkMode ? "#4a5568" : "#f9fafb",
    color: darkMode ? "#e2e8f0" : "#1a1a1a",
  };

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h1 style={{ fontSize: "1.5rem", fontWeight: "bold", marginBottom: "1rem", textAlign: "center", ...textStyle }}>
          Integrating Logical Constraints In Multimodal AI Assistant
        </h1>

        {/* Dark Mode Toggle Button */}
        <button
          onClick={toggleDarkMode}
          style={{
            position: "absolute",
            top: "1rem",
            right: "1rem",
            padding: "0.5rem 1rem",
            backgroundColor: darkMode ? "#4a90e2" : "#e2e8f0",
            color: darkMode ? "#fff" : "#1a1a1a",
            border: "none",
            borderRadius: "0.25rem",
            cursor: "pointer",
            transition: "background-color 0.3s",
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = darkMode ? "#357abd" : "#d1d5db"}
          onMouseOut={(e) => e.target.style.backgroundColor = darkMode ? "#4a90e2" : "#e2e8f0"}
        >
          {darkMode ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        {/* Mode selection */}
        <div style={{ marginBottom: "1rem" }}>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: "500", marginBottom: "0.5rem", ...textStyle }}>
            Select Mode:
          </label>
          <select value={mode} onChange={(e) => setMode(e.target.value)} style={selectStyle}>
            <option value="text1">Single Agent LLM Text Response Generation</option>
            <option value="text2">Multi Agent LLMs Text Response Generation</option>
            <option value="image">Image Generation</option>
          </select>
        </div>

        {(mode === "text1" || mode === "text2") && (
          <input
            type="text"
            placeholder="Enter your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            style={inputStyle}
          />
        )}

        <ConstraintInput logicalGroups={logicalGroups} setLogicalGroups={setLogicalGroups} mode={mode} />

        <ReactMediaRecorder
          audio
          onStop={(blobUrl, blob) => {
            handleTranscription(blob);
            setRecordingTime(0);
          }}
          render={({ status, startRecording, stopRecording }) => (
            <div style={{ marginBottom: "1rem", position: "relative" }}>
              {(mode === "text1" || mode === "text2") && (
                <p style={{ marginBottom: "0.5rem", fontWeight: "500", ...textStyle }}>
                  Mic Status: <span style={{ color: status === "recording" ? "#34d399" : textStyle.color }}>{status}</span>
                  {status === "recording" && ` (${Math.floor(recordingTime / 60)}:${(recordingTime % 60).toString().padStart(2, "0")})`}
                </p>
              )}
              {(mode === "text1" || mode === "text2") && (
                <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                  <button
                    onClick={() => {
                      startRecording();
                      setRecordingTime(1);
                      if (waveform) {
                        waveform.stop();
                        waveform.empty();
                        setIsWaveformReady(false);
                      }
                    }}
                    style={{
                      padding: "0.5rem 1rem",
                      background: "linear-gradient(135deg, #34d399, #10b981)",
                      color: "#fff",
                      border: "none",
                      borderRadius: "8px",
                      boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
                      transition: "transform 0.2s, box-shadow 0.2s",
                      cursor: "pointer",
                    }}
                    onMouseOver={(e) => e.target.style.transform = "scale(1.05)"}
                    onMouseOut={(e) => e.target.style.transform = "scale(1)"}
                  >
                    🎙️ Start Recording
                  </button>
                  <button
                    onClick={stopRecording}
                    style={{
                      padding: "0.5rem 1rem",
                      background: "linear-gradient(135deg, #f87171, #ef4444)",
                      color: "#fff",
                      border: "none",
                      borderRadius: "8px",
                      boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
                      transition: "transform 0.2s, box-shadow 0.2s",
                      cursor: "pointer",
                    }}
                    onMouseOver={(e) => e.target.style.transform = "scale(1.05)"}
                    onMouseOut={(e) => e.target.style.transform = "scale(1)"}
                  >
                    ⏹️ Stop & Transcribe
                  </button>
                  {waveform && isWaveformReady && (
                    <button
                      onClick={() => waveform.playPause()}
                      style={{
                        padding: "0.5rem 1rem",
                        background: "linear-gradient(135deg, #4a90e2, #357abd)",
                        color: "#fff",
                        border: "none",
                        borderRadius: "8px",
                        boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
                        transition: "transform 0.2s, box-shadow 0.2s",
                        cursor: "pointer",
                      }}
                      onMouseOver={(e) => e.target.style.transform = "scale(1.05)"}
                      onMouseOut={(e) => e.target.style.transform = "scale(1)"}
                    >
                      {isPlaying ? "⏸️ Pause" : "▶️ Play"}
                    </button>
                  )}
                </div>
              )}
              <div ref={waveformRef} style={{ marginTop: "0.5rem" }} />
            </div>
          )}
        />

        <button
          onClick={mode === "text1" ? handleGenerateResponse1 : mode === "text2" ? handleGenerateResponse2 : handleGenerateImage}
          style={{
            padding: "0.75rem",
            color: "#ffffff",
            borderRadius: "0.25rem",
            width: "100%",
            backgroundColor: isLoading ? "#9ca3af" : "#4a90e2",
            cursor: isLoading ? "not-allowed" : "pointer",
            transition: "background-color 0.2s",
            marginBottom: "1rem",
            border: "none",
            fontSize: "1rem",
            fontWeight: "500",
          }}
          disabled={isLoading}
          onMouseOver={(e) => !isLoading && (e.target.style.backgroundColor = "#357abd")}
          onMouseOut={(e) => !isLoading && (e.target.style.backgroundColor = "#4a90e2")}
        >
          {isLoading ? "Generating..." : `Generate ${mode === "text1" || mode === "text2" ? "Response" : "Image"}`}
        </button>

        {isLoading && (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", marginTop: "1rem", gap: "0.75rem" }}>
            <div
              style={{
                width: "1.25rem",
                height: "1.25rem",
                border: `3px solid ${darkMode ? "#60a5fa" : "#2563eb"}`,
                borderTopColor: "transparent",
                borderRadius: "50%",
                animation: "spin 0.8s linear infinite",
              }}
            ></div>
            <span
              style={{
                fontSize: "0.875rem",
                fontWeight: "600",
                color: darkMode ? "#bfdbfe" : "#1e40af",
                letterSpacing: "0.025em",
                display: "flex",
                alignItems: "center",
              }}
            >
              {mode === "text1" || mode === "text2" ? `Thinking for ${loadingSeconds}s` : `Crafting image for ${loadingSeconds}s`}
            </span>
          </div>
        )}

        {mode === "text1" && <ResponseDisplay response={response} maleSpeaker={maleSpeaker} onSpeak={handleSpeakResponse} responseTime={responseTime} iterationCount={iterationCount} />}

        {mode === "text2" && (responseA || responseB) && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {responseA && (
              <ResponseDisplay
                response={responseA}
                analysis={analysisBofA}
                modelName="Model A (Gemini)"
                maleSpeaker={maleSpeaker}
                onSpeak={handleSpeakResponse}
                responseTime={responseTime}
                iterationCount={0}
              />
            )}
            {responseB && (
              <ResponseDisplay
                response={responseB}
                analysis={analysisAofB}
                modelName="Model B (DeepSeek)"
                maleSpeaker={maleSpeaker}
                onSpeak={handleSpeakResponse}
                responseTime={responseTime}
                iterationCount={0}
              />
            )}
          </div>
        )}

        {mode === "text1" && response && <KnowledgeGraphDisplay response={response} />}

        {mode === "image" && image && (
          <div style={{ marginTop: "1rem", padding: "1rem", border: `1px solid ${darkMode ? "#4a5568" : "#e2e8f0"}`, borderRadius: "0.25rem", backgroundColor: darkMode ? "#2d3748" : "#f9fafb" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
              <h2 style={{ fontSize: "1.125rem", fontWeight: "600", ...textStyle }}>Generated Image:</h2>
              <span
                style={{
                  fontSize: "0.875rem",
                  fontWeight: "500",
                  padding: "0.25rem 0.5rem",
                  borderRadius: "0.25rem",
                  opacity: 0,
                  backgroundColor: "#e0f7fa",
                  color: "#00796b",
                  animation: "fadeIn 0.5s ease-in forwards",
                }}
              >
                Crafted for {imageGenerationTime}s
              </span>
            </div>
            <img src={`data:image/png;base64,${image}`} alt="Generated" style={{ width: "100%", marginBottom: "1rem", borderRadius: "0.25rem" }} />
            <button
              onClick={handleDownloadImage}
              style={{
                padding: "0.75rem",
                backgroundColor: "#4a90e2",
                color: "#ffffff",
                borderRadius: "0.25rem",
                width: "100%",
                transition: "background-color 0.2s",
                border: "none",
                fontSize: "1rem",
                fontWeight: "500",
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = "#357abd"}
              onMouseOut={(e) => e.target.style.backgroundColor = "#4a90e2"}
            >
              Download Image
            </button>
          </div>
        )}
      </div>
      <style>
        {`
          @keyframes pulse {
            0% { transform: translateX(-50%) scale(1); opacity: 1; }
            100% { transform: translateX(-50%) scale(1.5); opacity: 0; }
          }
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
          @keyframes fadeIn {
            to { opacity: 1; }
          }
        `}
      </style>
    </div>
  );
}