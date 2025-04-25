import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import mermaid from "mermaid";
import katex from "katex";
import "katex/dist/katex.min.css";

// Initialize Mermaid
mermaid.initialize({
  startOnLoad: false,
  securityLevel: "loose",
  theme: "default",
});

const KnowledgeGraphDisplay = ({ response, minZoom = 0.1, maxZoom = 5, zoomStep = 0.25 }) => {
  const [svgContent, setSvgContent] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [triples, setTriples] = useState([]); // Store triples for DL conversion
  const containerRef = useRef(null);

  // Fetch and render Mermaid graph
  useEffect(() => {
    if (!response) return;
    setLoading(true);
    setError(null);
    setSvgContent("");
    setTriples([]); // Reset triples

    axios
      .post("http://localhost:8000/api/generate-knowledge-graph", { response })
      .then(async (res) => {
        const fetchedTriples = res.data.triples;
        setTriples(fetchedTriples); // Update the triples state
        const nodes = new Set();
        const edges = fetchedTriples.map(([e1, rel, e2]) => {
          const id1 = e1.replace(/[^\w]/g, "_");
          const id2 = e2.replace(/[^\w]/g, "_");
          const r = rel.replace(/[^\w]/g, "_");
          nodes.add(id1);
          nodes.add(id2);
          return `${id1} --> |${r}| ${id2}`;
        });
        const def = `graph TD\n${[...nodes]
          .map((id) => `${id}["${id.replace(/_/g, " ")}"]`)
          .join("\n")}\n${edges.join("\n")}`;
        const { svg } = await mermaid.render(`graph-${Date.now()}`, def);
        setSvgContent(svg);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || err.message || "Failed to fetch graph");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [response]);

  // Render SVG and size container to full graph width
  useEffect(() => {
    if (!svgContent || !containerRef.current) return;
    containerRef.current.innerHTML = svgContent;
    const svgEl = containerRef.current.querySelector("svg");
    if (!svgEl) return;

    const vb = svgEl.getAttribute("viewBox").split(" ").map(Number);
    const [,, vbWidth, vbHeight] = vb;

    svgEl.setAttribute("width", vbWidth);
    svgEl.setAttribute("height", vbHeight);
    svgEl.setAttribute("preserveAspectRatio", "xMinYMid meet");

    containerRef.current.style.width = `${vbWidth}px`;
    containerRef.current.style.height = `${vbHeight}px`;
  }, [svgContent]);

  // Convert triples to Description Logics (DL) with all ALC constructs
  const convertToDL = (triples) => {
    if (!triples || triples.length === 0) return [];

    // Extract all entities (both entity1 and entity2)
    const allEntities = new Set();
    triples.forEach(([e1, , e2]) => {
      allEntities.add(e1);
      allEntities.add(e2);
    });

    // Group triples by entity1 to handle multiple relations
    const groupedByEntity1 = triples.reduce((acc, [e1, rel, e2]) => {
      if (!acc[e1]) acc[e1] = [];
      acc[e1].push([rel, e2]);
      return acc;
    }, {});

    // Group triples by entity1 and relation to identify unions (⊔)
    const groupedByEntity1AndRelation = triples.reduce((acc, [e1, rel, e2]) => {
      if (!acc[e1]) acc[e1] = {};
      if (!acc[e1][rel]) acc[e1][rel] = [];
      acc[e1][rel].push(e2);
      return acc;
    }, {});

    const dlExpressions = [];

    // Process each entity1
    Object.entries(groupedByEntity1).forEach(([entity1, relations]) => {
      const entity1Concept = entity1.charAt(0).toUpperCase() + entity1.slice(1).replace(/\s/g, "");

      // Process relations for this entity1
      const restrictions = [];
      Object.entries(groupedByEntity1AndRelation[entity1]).forEach(([rel, entities]) => {
        const relationRole = rel.replace(/\s/g, "");

        // Handle union (⊔) if there are multiple entities for the same relation
        const entityConcepts = entities.map((e2) => {
          return e2.charAt(0).toUpperCase() + e2.slice(1).replace(/\s/g, "");
        });

        // Existential restriction (∃)
        const existentialPart = entityConcepts.length > 1
          ? `\\exists ${relationRole}.(${entityConcepts.join(" \\sqcup ")})`
          : `\\exists ${relationRole}.${entityConcepts[0]}`;

        // Universal restriction (∀)
        const universalPart = entityConcepts.length > 1
          ? `\\forall ${relationRole}.(${entityConcepts.join(" \\sqcup ")})`
          : `\\forall ${relationRole}.${entityConcepts[0]}`;

        // Combine ∃ and ∀ with intersection (⊓)
        restrictions.push(`(${existentialPart} \\sqcap ${universalPart})`);
      });

      // Combine all restrictions with intersection (⊓) if there are multiple relations
      const combinedRestrictions = restrictions.length > 1
        ? `(${restrictions.join(" \\sqcap ")})`
        : restrictions[0];

      // Add the main expression: Entity1 ⊑ CombinedRestrictions
      dlExpressions.push(`${entity1Concept} \\sqsubseteq ${combinedRestrictions}`);

      // Add a negation (¬) example: Entity1 is not related to another entity via a hypothetical relation
      const allRelations = new Set(triples.map(([, rel]) => rel));
      const entityRelations = new Set(relations.map(([rel]) => rel));
      const unusedRelation = [...allRelations].find((rel) => !entityRelations.has(rel));
      if (unusedRelation) {
        const someOtherEntity = [...allEntities].find((e) => e !== entity1);
        if (someOtherEntity) {
          const otherEntityConcept = someOtherEntity.charAt(0).toUpperCase() + someOtherEntity.slice(1).replace(/\s/g, "");
          const unusedRelationRole = unusedRelation.replace(/\s/g, "");
          dlExpressions.push(`${entity1Concept} \\sqsubseteq \\neg \\exists ${unusedRelationRole}.${otherEntityConcept}`);
        }
      }
    });

    // Add ⊤ for an entity to demonstrate
    if (triples.length > 0) {
      const firstEntity = triples[0][0];
      const firstEntityConcept = firstEntity.charAt(0).toUpperCase() + firstEntity.slice(1).replace(/\s/g, "");
      const someRelation = triples[0][1].replace(/\s/g, "");
      dlExpressions.push(`${firstEntityConcept} \\sqsubseteq \\forall ${someRelation}.\\top`);
    }

    return dlExpressions;
  };

  const dlExpressions = convertToDL(triples);

  const handleZoomIn = () => {
    setZoomLevel((z) => Math.min(z + zoomStep, maxZoom));
  };

  const handleZoomOut = () => {
    setZoomLevel((z) => Math.max(z - zoomStep, minZoom));
  };

  return (
    <div
      style={{
        marginTop: "1rem",
        padding: "1rem",
        border: "1px solid #e2e8f0",
        borderRadius: "0.25rem",
        backgroundColor: "#f9fafb",
        display: "flex",
        flexDirection: "column",
        width: "93.5%",
        height: "100%",
      }}
    >
      {/* Knowledge Graph Visualization */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
        <h3
          style={{
            fontSize: "1.125rem",
            fontWeight: "600",
            color: "#1a1a1a",
            margin: 0,
          }}
        >
          Knowledge Graph:
        </h3>

        {svgContent && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <button
              onClick={handleZoomOut}
              style={{
                padding: "0.25rem 0.75rem",
                backgroundColor: "#4a90e2",
                color: "#fff",
                border: "none",
                borderRadius: "0.25rem",
                cursor: "pointer",
                transition: "background-color 0.2s",
                fontSize: "1rem",
              }}
              onMouseOver={(e) => (e.target.style.backgroundColor = "#357abd")}
              onMouseOut={(e) => (e.target.style.backgroundColor = "#4a90e2")}
            >
              −
            </button>
            <span
              style={{
                fontSize: "0.875rem",
                fontWeight: "500",
                padding: "0.25rem 0.5rem",
                borderRadius: "0.25rem",
                backgroundColor: "#e0f7fa",
                color: "#00796b",
              }}
            >
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={handleZoomIn}
              style={{
                padding: "0.25rem 0.75rem",
                backgroundColor: "#4a90e2",
                color: "#fff",
                border: "none",
                borderRadius: "0.25rem",
                cursor: "pointer",
                transition: "background-color 0.2s",
                fontSize: "1rem",
              }}
              onMouseOver={(e) => (e.target.style.backgroundColor = "#357abd")}
              onMouseOut={(e) => (e.target.style.backgroundColor = "#4a90e2")}
            >
              +
            </button>
          </div>
        )}
      </div>

      {loading && (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", padding: "1rem" }}>
          <div
            style={{
              width: "1.5rem",
              height: "1.5rem",
              border: "3px solid #4b5563",
              borderTopColor: "transparent",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
              marginRight: "0.5rem",
            }}
          />
          <p style={{ color: "#4b5563", margin: 0 }}>Loading knowledge graph...</p>
        </div>
      )}
      {error && (
        <p style={{ color: "#ef4444", padding: "1rem", textAlign: "center", margin: 0 }}>
          Error: {error}
        </p>
      )}

      <div
        style={{
          flexGrow: 1,
          overflowX: "auto",
          overflowY: "hidden",
          background: "#ffffff",
          border: "1px solid #e2e8f0",
          borderRadius: "0.25rem",
          position: "relative",
        }}
      >
        <div
          style={{
            transform: `scale(${zoomLevel})`,
            transformOrigin: "left center",
            transition: "transform 0.2s ease-in-out",
          }}
        >
          <div ref={containerRef} style={{ display: "inline-block" }} />
        </div>
      </div>

      {/* Description Logics (DL) Representation */}
      {dlExpressions.length > 0 && (
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            border: "1px solid #e2e8f0",
            borderRadius: "0.25rem",
            backgroundColor: "#ffffff",
            width: "100%", // Match the outer container's width
            boxSizing: "border-box", // Ensure padding doesn't cause overflow
          }}
        >
          <h3
            style={{
              fontSize: "1.125rem",
              fontWeight: "600",
              color: "#1a1a1a",
              marginBottom: "0.5rem",
            }}
          >
            Description Logics Representation:
          </h3>
          <ul
            style={{
              listStyleType: "none",
              paddingLeft: "1rem",
              margin: 0,
              overflow: "hidden", // Prevent scrollbar
            }}
          >
            {dlExpressions.map((expression, index) => (
              <li
                key={index}
                style={{
                  color: "#4b5563",
                  marginBottom: "0.5rem",
                  lineHeight: "1.5",
                  wordBreak: "break-all", // Allow breaking within words if necessary
                  overflowWrap: "break-word", // Ensure text wraps within the container
                }}
                dangerouslySetInnerHTML={{
                  __html: katex.renderToString(expression, {
                    throwOnError: false,
                    output: "html",
                  }),
                }}
              />
            ))}
          </ul>
        </div>
      )}

      <style>
        {`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
          .katex {
            white-space: normal !important; /* Allow KaTeX content to wrap */
            display: inline !important; /* Ensure KaTeX content behaves as inline */
          }
        `}
      </style>
    </div>
  );
};

export default KnowledgeGraphDisplay;