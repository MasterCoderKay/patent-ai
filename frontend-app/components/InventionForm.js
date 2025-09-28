import { useState } from "react";

export default function InventionForm({ onSubmit, loading }) {
  const [idea, setIdea] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!idea.trim()) return;
    onSubmit(idea);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 w-full max-w-lg bg-white p-6 rounded shadow-md"
    >
      <textarea
        className="border rounded p-2"
        rows={4}
        placeholder="Describe your invention idea..."
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
      />
      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Analyze Idea"}
      </button>
    </form>
  );
}
