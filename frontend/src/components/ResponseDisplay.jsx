import { useState, useRef } from "react";

export default function ResponseDisplay({ response, analysis, modelName, maleSpeaker, onSpeak, responseTime, iterationCount }) {
  const [isSpeaking, setIsSpeaking] = useState(false); // Track loading state
  const [isPlaying, setIsPlaying] = useState(false); // Track audio playback
  const audioRef = useRef(null); // Store Audio object

  const handleSpeak = async () => {
    setIsSpeaking(true); // Start loading
    try {
      const { audio, url } = await enhancedOnSpeak(response, () => {
        setIsSpeaking(false); // Stop loading
      });
      audioRef.current = audio;
      audioRef.current.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioRef.current.src);
        audioRef.current = null;
      };
      audioRef.current.onerror = () => {
        setIsPlaying(false);
        setIsSpeaking(false);
        audioRef.current = null;
      };
      audioRef.current.play();
      setIsPlaying(true); // Audio is playing
    } catch (error) {
      console.error("TTS failed:", error);
      setIsSpeaking(false);
      setIsPlaying(false);
    }
  };

  const handleStopSpeak = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0; // Reset to start
      URL.revokeObjectURL(audioRef.current.src);
      audioRef.current = null;
    }
    setIsPlaying(false);
  };

  const enhancedOnSpeak = async (text, callback) => {
    const res = await onSpeak(text, callback);
    return res; // Expect { audio, url } from handleSpeakResponse
  };

  // Parse response into a list of points
const renderResponsePoints = (text) => {
  if (!text) return null;

  // Trim off any leading/trailing whitespace
  // then split only on NEWLINE + number-dot-space
  const points = text
    .trim()
    .split(/\n(?=\d+\.\s)/)
    .filter((point) => point.trim());

  return (
    <ul style={{ listStyleType: "none", paddingLeft: 0, margin: 0 }}>
      {points.map((point, index) => {
        const match = point.match(/^(\d+\.\s)(.*)$/);
        const numberPrefix = match ? match[1] : "";
        const content = match ? match[2] : point.trim();

        return (
          <li
            key={index}
            style={{
              color: "#1a1a1a",
              marginBottom: "0.5rem",
              lineHeight: "1.5",
              display: "flex",
              alignItems: "flex-start",
              gap: "0.25rem",
            }}
          >
            {numberPrefix && (
              <span style={{ whiteSpace: "nowrap" }}>
                {numberPrefix}
              </span>
            )}
            <span style={{ flex: 1 }}>
              {content}
            </span>
          </li>
        );
      })}
    </ul>
  );
};


  // Parse analysis into sections and sub-points
  const renderAnalysisSections = (text) => {
    if (!text) return null;

    // Split by main sections
    const sections = text.split(/(STRENGTHS:|WEAKNESSES:|POTENTIAL IMPROVEMENTS:|ANALYSIS OF QUESTIONS:)/i).filter((section) => section.trim());
    const sectionContent = {};

    // Group sections and their content, consolidating duplicates
    let currentSection = "";
    for (let i = 0; i < sections.length; i++) {
      const section = sections[i];
      const normalizedSection = section.toUpperCase();
      if (["STRENGTHS:", "WEAKNESSES:", "POTENTIAL IMPROVEMENTS:", "ANALYSIS OF QUESTIONS:"].includes(normalizedSection)) {
        currentSection = section;
        if (i + 1 < sections.length) {
          if (sectionContent[currentSection]) {
            sectionContent[currentSection] += `\n${sections[i + 1]}`;
          } else {
            sectionContent[currentSection] = sections[i + 1];
          }
        }
        i++; // Skip the next item as it's the content
      }
    }

    // Ensure all expected sections are present
    const expectedSections = ["STRENGTHS:", "WEAKNESSES:", "POTENTIAL IMPROVEMENTS:"];
    expectedSections.forEach((section) => {
      if (!sectionContent[section]) {
        sectionContent[section] = "None identified.";
      }
    });

    // Normalize content: Convert narrative text into bullet points if needed
    const normalizeContent = (content) => {
      const lines = content.split(/\n/).filter((line) => line.trim());
      const normalizedLines = lines.map((line) => {
        if (!line.match(/^\s*[-✓✗]\s/)) {
          return `- ${line.trim()}`;
        }
        return line.trim();
      });
      return normalizedLines.join("\n");
    };

    return (
      <div>
        {Object.keys(sectionContent).map((header, index) => {
          const normalizedSection = header.toUpperCase();

          // Skip "ANALYSIS OF QUESTIONS" for now; we'll handle it separately
          if (normalizedSection === "ANALYSIS OF QUESTIONS:") {
            return null;
          }

          const content = normalizeContent(sectionContent[header]);

          return (
            <div key={index}>
              <h4
                style={{
                  fontSize: "0.95rem",
                  fontWeight: "600",
                  color: "#1a1a1a",
                  marginTop: "0.5rem",
                  marginBottom: "0.25rem",
                }}
              >
                {header.charAt(0).toUpperCase() + header.slice(1).toLowerCase()}
              </h4>
              {content.trim() === "None identified." ? (
                <p style={{ color: "#4b5563", fontStyle: "italic", paddingLeft: "1rem", margin: 0 }}>
                  None identified.
                </p>
              ) : (
                <ul style={{ listStyleType: "none", paddingLeft: "1rem", margin: 0 }}>
                  {content.split(/\n/).filter((point) => {
                    const trimmedPoint = point.trim();
                    return trimmedPoint.length > 1 && trimmedPoint !== "-";
                  }).map((subPoint, subIndex) => {
                    const hasCheck = subPoint.includes("✓");
                    const hasCross = subPoint.includes("✗");
                    const marker = hasCheck ? "✓" : hasCross ? "✗" : null;
                    const cleanedSubPoint = subPoint.replace("✓", "").replace("✗", "").replace(/^-\s*/, "").trim();

                    return (
                      <li
                        key={subIndex}
                        style={{
                          color: "#4b5563",
                          marginBottom: "0.25rem",
                          lineHeight: "1.4",
                          display: "flex",
                          alignItems: "flex-start",
                          gap: "0.5rem",
                        }}
                      >
                        {marker && (
                          <span
                            style={{
                              color: marker === "✓" ? "#10b981" : "#ef4444",
                              fontSize: "1.1rem",
                              lineHeight: "1",
                            }}
                          >
                            {marker}
                          </span>
                        )}
                        <span style={{ fontStyle: "italic" }}>{cleanedSubPoint}</span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          );
        })}

        {/* Handle "ANALYSIS OF QUESTIONS" separately */}
        {sectionContent["ANALYSIS OF QUESTIONS:"] && (
          <div>
            <h4
              style={{
                fontSize: "0.95rem",
                fontWeight: "600",
                color: "#1a1a1a",
                marginTop: "0.5rem",
                marginBottom: "0.25rem",
              }}
            >
              Analysis Summary:
            </h4>
            <ul style={{ listStyleType: "none", paddingLeft: "1rem", margin: 0 }}>
              {(() => {
                // Normalize the content by ensuring consistent formatting
                const content = sectionContent["ANALYSIS OF QUESTIONS:"]
                  .replace(/\n+/g, "\n") // Replace multiple newlines with a single newline
                  .replace(/(\d+\.)([^\s])/, "$1 $2") // Ensure a space after the number and dot (e.g., "10." -> "10. ")
                  .trim();

                // Split by numbered points, ensuring numbers like "10.", "11.", etc., are handled
                const points = content.split(/(?=\d+\.\s)/).filter((point) => point.trim());

                return points.length > 0 ? points.map((point, subIndex) => {
                  // Split the point into the number prefix (e.g., "10. ") and the content
                  const match = point.match(/^(\d+\.\s)(.*)$/);
                  const numberPrefix = match ? match[1] : "";
                  const content = match ? match[2] : point.trim();

                  return (
                    <li
                      key={subIndex}
                      style={{
                        color: "#4b5563",
                        marginBottom: "0.25rem",
                        lineHeight: "1.4",
                        fontStyle: "italic",
                        display: "flex",
                        alignItems: "flex-start",
                        gap: "0.25rem",
                      }}
                    >
                      {numberPrefix && (
                        <span style={{ whiteSpace: "nowrap" }}>
                          {numberPrefix}
                        </span>
                      )}
                      <span style={{ flex: 1 }}>
                        {content}
                      </span>
                    </li>
                  );
                }) : (
                  <li
                    style={{
                      color: "#4b5563",
                      marginBottom: "0.25rem",
                      lineHeight: "1.4",
                      fontStyle: "italic",
                    }}
                  >
                    No analysis points provided.
                  </li>
                );
              })()}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return response ? (
    <div style={{ marginTop: "1rem", padding: "1rem", border: "1px solid #e2e8f0", borderRadius: "0.25rem", backgroundColor: "#f9fafb" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
        <h2 style={{ fontSize: "1.125rem", fontWeight: "600"}}>{modelName ? `${modelName} Response` : "Generated Response"}:</h2>
        <div style={{ display: "flex", gap: "0.5rem" }}>
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
            Thought for {responseTime}s
          </span>
          {!analysis && (
            <span
              style={{
                fontSize: "0.875rem",
                fontWeight: "500",
                padding: "0.25rem 0.5rem",
                borderRadius: "0.25rem",
                opacity: "0",
                backgroundColor: "#e0f7fa",
                color: "#00796b",
                animation: "fadeIn 0.5s ease-in 0.2s forwards",
              }}
            >
              Refined {iterationCount}x
            </span>
          )}
        </div>
      </div>      
      {renderResponsePoints(response)}
      {analysis && (
        <>
          <h2 style={{ fontSize: "1.125rem", fontWeight: "600", color: "black", marginBottom: "0.5rem", paddingBottom: "0.5rem"}}>
            Analysis by {modelName === "Model A (Gemini)" ? "DeepSeek" : "Gemini"} for{" "}
            {modelName === "Model A (Gemini)" ? "Gemini" : "DeepSeek"} Response:
          </h2>
          {renderAnalysisSections(analysis)}
        </>
      )}
      <button
        onClick={isPlaying ? handleStopSpeak : handleSpeak}
        disabled={isSpeaking}
        style={{
          marginTop: "0.5rem",
          padding: "0.5rem",
          backgroundColor: isSpeaking ? "#9ca3af" : isPlaying ? "#ef4444" : "#4a90e2",
          color: "#fff",
          border: "none",
          borderRadius: "0.25rem",
          cursor: isSpeaking ? "not-allowed" : "pointer",
          transition: "background-color 0.2s",
          position: "relative",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "0.5rem",
        }}
        onMouseOver={(e) => !isSpeaking && (e.target.style.backgroundColor = isPlaying ? "#b91c1c" : "#357abd")}
        onMouseOut={(e) => !isSpeaking && (e.target.style.backgroundColor = isPlaying ? "#ef4444" : "#4a90e2")}
      >
        {isSpeaking ? (
          <>
            <div
              style={{
                width: "1rem",
                height: "1rem",
                border: "2px solid #fff",
                borderTopColor: "transparent",
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
              }}
            />
            Loading...
          </>
        ) : isPlaying ? (
          "⏹️ Stop Speaking"
        ) : (
          "🔊 Listen"
        )}
      </button>
      <style>
        {`
          @keyframes fadeIn {
            to { opacity: 1; }
          }
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  ) : null;
}