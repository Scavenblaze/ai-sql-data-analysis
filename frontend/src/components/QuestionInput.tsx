import { useState } from "react";

interface QuestionInputProps {
  onSubmit: (question: string) => void;
  loading: boolean;
}

export default function QuestionInput({onSubmit, loading}: QuestionInputProps) {
  const [question, setQuestion] = useState("");

  const handleSubmit = (event: React.SubmitEvent) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if(!trimmedQuestion || loading){
      return;
    }

    onSubmit(trimmedQuestion);
  }

  return(
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex gap-3">
        <input
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask a question about your data..."
          disabled={loading}
          className="flex-1 rounded-lg border border-gray-300 px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-gray-100"
        />

        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>
    </form>
  );
}