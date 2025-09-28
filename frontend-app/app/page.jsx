"use client";
import { useState } from "react";

export default function Home() {
  const [idea, setIdea] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

  const handleAnalyze = async () => {
    if (!idea.trim()) return;
    setLoading(true);
    setAnalysis(null);

    try {
      const res = await Promise.all([
        fetch(`${backendUrl}/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ idea }),
        }),
        fetch(`${backendUrl}/score`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ idea }),
        }),
        fetch(`${backendUrl}/keywords`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ idea }),
        }),
        fetch(`${backendUrl}/market-pitch`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ idea }),
        }),
      ]);

      const data = await Promise.all(res.map(r => r.json()));
      setAnalysis({
        analysis: data[0].analysis,
        score: data[1].novelty_score,
        keywords: data[2].keywords,
        pitch: data[3].pitch,
      });
    } catch (error) {
      console.error("Error analyzing idea:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-gray-100">
      <h1 className="text-4xl font-bold mb-6">PatentAI</h1>
      <textarea
        className="w-full max-w-lg p-4 border rounded-lg mb-4"
        rows="5"
        placeholder="Describe your invention idea..."
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
      />
      <button
        onClick={handleAnalyze}
        disabled={loading}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Analyze Idea"}
      </button>

      {analysis && (
        <div className="mt-6 w-full max-w-2xl bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-semibold mb-4">Results</h2>
          <p><strong>Analysis:</strong> {analysis.analysis}</p>
          <p><strong>Novelty Score:</strong> {analysis.score}</p>
          <p><strong>Keywords:</strong> {analysis.keywords?.join(", ")}</p>
          <p><strong>Market Pitch:</strong> {analysis.pitch}</p>
        </div>
      )}
    </main>
  );
}
