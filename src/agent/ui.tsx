import { useStreamContext } from "@langchain/langgraph-sdk/react-ui";
import { useEffect } from "react";
import ReactMarkdown from "react-markdown";

/**
 * Markdown Artifact Component
 * Renders a markdown document in the artifact side panel
 */
function MarkdownArtifactComponent(props: { content: string; title: string }) {
  const stream = useStreamContext();
  const artifactTuple = (stream as any).meta?.artifact;

  const [Artifact, bag] =
    artifactTuple && Array.isArray(artifactTuple) && artifactTuple.length >= 2
      ? artifactTuple
      : [null, null];
  const { open, setOpen } = bag || {};

  // Auto-open the artifact panel (only once, on mount)
  useEffect(() => {
    if (setOpen && !open) {
      setOpen(true);
    }
  }, [setOpen]);

  if (Artifact) {
    return (
      <>
        <div
          onClick={() => setOpen && setOpen(!open)}
          style={{
            margin: "12px 0",
            padding: "12px 16px",
            borderRadius: "8px",
            border: "1px solid #e5e7eb",
            backgroundColor: open ? "#eff6ff" : "#f9fafb",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <span style={{ fontSize: "20px" }}>📄</span>
          <div style={{ flex: 1 }}>
            <p style={{ fontWeight: 500, margin: 0, color: "#1f2937" }}>
              {props.title}
            </p>
            <p
              style={{ fontSize: "12px", margin: "2px 0 0 0", color: "#6b7280" }}
            >
              {open ? "Click to close" : "Click to open"}
            </p>
          </div>
          <span
            style={{
              color: "#6b7280",
              transform: open ? "rotate(90deg)" : "none",
              transition: "transform 0.2s",
            }}
          >
            ▶
          </span>
        </div>

        <Artifact title={props.title}>
          <div
            style={{
              padding: "24px",
              height: "100%",
              overflow: "auto",
              boxSizing: "border-box",
            }}
          >
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{props.content}</ReactMarkdown>
            </div>
          </div>
        </Artifact>
      </>
    );
  }

  // Fallback: render inline if artifact context is not available
  return (
    <div
      style={{
        margin: "12px 0",
        padding: "16px",
        borderRadius: "8px",
        border: "1px solid #e5e7eb",
        backgroundColor: "#f9fafb",
      }}
    >
      <h3
        style={{
          fontSize: "16px",
          fontWeight: 600,
          marginBottom: "12px",
          color: "#1f2937",
        }}
      >
        📄 {props.title}
      </h3>
      <div
        style={{
          backgroundColor: "white",
          padding: "12px",
          borderRadius: "6px",
          border: "1px solid #e5e7eb",
        }}
      >
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown>{props.content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default {
  markdown_artifact: MarkdownArtifactComponent,
};
