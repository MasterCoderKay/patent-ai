import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";

function App() {
  const [newClaim, setNewClaim] = useState("");
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API_BASE = "http://127.0.0.1:8000"; // FastAPI backend

  // Load history on mount
  useEffect(() => {
    fetch(`${API_BASE}/history`)
      .then((res) => res.json())
      .then((data) => setHistory(data))
      .catch((err) => console.error("Failed to fetch history:", err));
  }, []);

  const submitClaim = async () => {
    if (!newClaim.trim()) return;

    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE}/polish-claim`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claim: newClaim }),
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();
      const entry = { original: newClaim, polished: data.result };
      setSelectedClaim(entry);
      setHistory((prev) => [...prev, entry]);
      setNewClaim("");
    } catch (err) {
      console.error("Error:", err);
      setError("Failed to polish claim. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "Arial, sans-serif" }}>
      {/* Left Panel: History */}
      <div
        style={{
          width: "300px",
          borderRight: "1px solid #ddd",
          padding: "20px",
          overflowY: "auto",
        }}
      >
        <h2>History</h2>
        {history.length === 0 && <p>No history yet</p>}
        {history.map((item, idx) => (
          <div
            key={idx}
            onClick={() => setSelectedClaim(item)}
            style={{
              padding: "10px",
              marginBottom: "10px",
              border: "1px solid #eee",
              borderRadius: "6px",
              cursor: "pointer",
              background: selectedClaim === item ? "#f0f0f0" : "#fff",
            }}
          >
            {item.original.length > 40
              ? item.original.slice(0, 40) + "..."
              : item.original}
          </div>
        ))}
      </div>

      {/* Right Panel: Input & Result */}
      <div style={{ flex: 1, padding: "20px", overflowY: "auto" }}>
        <h2>Enter New Claim</h2>
        <textarea
          value={newClaim}
          onChange={(e) => setNewClaim(e.target.value)}
          placeholder="Type your claim here..."
          style={{ width: "100%", height: "100px", padding: "10px", fontSize: "14px" }}
        />
        <br />
        <button
          onClick={submitClaim}
          disabled={loading}
          style={{
            marginTop: "10px",
            padding: "10px 20px",
            fontSize: "14px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Polishing..." : "Submit"}
        </button>

        {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}

        <hr style={{ margin: "20px 0" }} />

        {selectedClaim ? (
          <>
            <h2>Original Claim</h2>
            <p>{selectedClaim.original}</p>

            <h2>Polished Claim</h2>
            <div
              style={{
                background: "#f9f9f9",
                padding: "15px",
                borderRadius: "8px",
                border: "1px solid #ddd",
              }}
            >
              <ReactMarkdown>{selectedClaim.polished}</ReactMarkdown>
            </div>
          </>
        ) : (
          <p>Select a claim from history to view details</p>
        )}
      </div>
    </div>
  );
}

export default App;
