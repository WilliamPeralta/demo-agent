import { useStreamContext } from "@langchain/langgraph-sdk/react-ui";

/**
 * Markdown Artifact Component
 * Renders a markdown document in the artifact side panel
 */
function MarkdownArtifactComponent(props: { content: string; title: string }) {
  const stream = useStreamContext();
  const artifactTuple = (stream as any).meta?.artifact;

  if (artifactTuple && Array.isArray(artifactTuple) && artifactTuple.length >= 2) {
    const [Artifact, bag] = artifactTuple;
    const { open, setOpen } = bag || {};

    // Auto-open the artifact panel
    if (setOpen && !open) {
      setOpen(true);
    }

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
            <p style={{ fontSize: "12px", margin: "2px 0 0 0", color: "#6b7280" }}>
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
          <div style={{ padding: "20px", height: "100%", overflow: "auto" }}>
            <SimpleMarkdown content={props.content} />
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
        <SimpleMarkdown content={props.content} />
      </div>
    </div>
  );
}

/**
 * Simple markdown renderer
 */
function SimpleMarkdown({ content }: { content: string }) {
  const lines = content.split("\n");

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", lineHeight: 1.6 }}>
      {lines.map((line, i) => {
        if (line.startsWith("# ")) {
          return (
            <h1
              key={i}
              style={{
                fontSize: "24px",
                fontWeight: "bold",
                margin: "20px 0 12px 0",
                borderBottom: "1px solid #e5e7eb",
                paddingBottom: "8px",
              }}
            >
              {line.slice(2)}
            </h1>
          );
        }
        if (line.startsWith("## ")) {
          return (
            <h2
              key={i}
              style={{
                fontSize: "20px",
                fontWeight: 600,
                margin: "16px 0 8px 0",
              }}
            >
              {line.slice(3)}
            </h2>
          );
        }
        if (line.startsWith("### ")) {
          return (
            <h3
              key={i}
              style={{
                fontSize: "16px",
                fontWeight: 500,
                margin: "12px 0 6px 0",
              }}
            >
              {line.slice(4)}
            </h3>
          );
        }
        if (line.startsWith("- ") || line.startsWith("* ")) {
          return (
            <li key={i} style={{ marginLeft: "20px", marginBottom: "4px" }}>
              {line.slice(2)}
            </li>
          );
        }
        if (line.trim() === "") {
          return <br key={i} />;
        }
        return (
          <p key={i} style={{ margin: "8px 0" }}>
            {line}
          </p>
        );
      })}
    </div>
  );
}

export default {
  markdown_artifact: MarkdownArtifactComponent,
};
