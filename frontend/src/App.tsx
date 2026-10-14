import { useRef, useState } from "react";

import QuestionInput from "./components/QuestionInput";
import ResultTable from "./components/ResultTable";
import ResultChart from "./components/ResultChart";

import { analyzeQuestion } from "./api/analyst";

import type { AnalysisResponse } from "./types/analysis";

const App = () =>{
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const requestId = useRef(0);
  const abortController = useRef<AbortController | null>(null);

  const handleQuestion = async (question: string) =>{
    const currentRequestId = ++requestId.current;
    const controller = new AbortController();

    abortController.current = controller;

    setLoading(true);
    setError(null);

    try{
      const response = await analyzeQuestion(question, controller.signal);

      if(currentRequestId !== requestId.current){
        return;
      }

      setResult(response);
    }catch(err){
      if(currentRequestId !== requestId.current){
        return;
      }

      if(controller.signal.aborted){
        return;
      }

      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    }finally{
      if(currentRequestId === requestId.current){
        abortController.current = null;
        setLoading(false);
      }
    }
  }

  const handleCancel = () =>{
    //invalidate this request so its response cannot update the UI
    requestId.current += 1;

    abortController.current?.abort();
    abortController.current = null;

    setLoading(false);
    setError(null);
  }

  return(
    <main className="min-h-screen bg-gray-50 px-4 py-8 sm:px-6 sm:py-12">
      <div className="mx-auto max-w-5xl">
        <header className="mb-8 sm:mb-10">
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
            SQL Data Analyst Agent
          </h1>

          <p className="mt-2 text-sm text-gray-600 sm:text-base">
            Ask questions about your data using natural language.
          </p>
        </header>

        <QuestionInput onSubmit={handleQuestion} loading={loading} />

        {loading && (
          <div
            role="status"
            aria-live="polite"
            className="mt-6 flex items-center justify-between gap-4 rounded-lg border border-blue-200 bg-blue-50 p-4"
          >
            <div className="flex items-center gap-3">
              <span className="h-5 w-5 shrink-0 animate-spin rounded-full border-2 border-blue-300 border-t-blue-700" />

              <p className="text-sm font-medium text-blue-800">
                Analyzing your question...
              </p>
            </div>

            <button
              type="button"
              onClick={handleCancel}
              className="shrink-0 rounded-md border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-700 transition hover:bg-red-50"
            >
              Cancel
            </button>
          </div>
        )}

        {error && (
          <div
            role="alert"
            className="mt-6 flex items-start justify-between gap-4 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700"
          >
            <p className="text-sm">{error}</p>

            <button
              type="button"
              onClick={() => setError(null)}
              aria-label="Dismiss error"
              className="shrink-0 rounded px-2 font-medium hover:bg-red-100"
            >
              x
            </button>
          </div>
        )}

        {result && (
          <section
            aria-label="Analysis results"
            className="mt-8 space-y-6"
          >
            <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm sm:p-6">
              <h2 className="text-lg font-semibold text-gray-900">
                Answer
              </h2>

              <p className="mt-3 whitespace-pre-wrap text-gray-700">
                {result.answer}
              </p>
            </div>

            <details className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
              <summary className="cursor-pointer px-5 py-4 font-medium text-gray-900 hover:bg-gray-50 sm:px-6">
                View generated SQL
              </summary>

              <pre className="overflow-x-auto border-t border-gray-200 bg-gray-50 p-5 text-sm text-gray-700 sm:p-6">
                <code>{result.sql}</code>
              </pre>
            </details>

            {result.chart && (
              <ResultChart
                rows={result.rows}
                chart={result.chart}
              />
            )}

            <section aria-labelledby="results-heading">
              <div className="mb-3 flex items-center justify-between gap-4">
                <h2
                  id="results-heading"
                  className="text-lg font-semibold text-gray-900"
                >
                  Results
                </h2>

                <span className="text-sm text-gray-500">
                  {result.row_count} rows
                </span>
              </div>

              <ResultTable rows={result.rows} />
            </section>
          </section>
        )}
      </div>
    </main>
  );
}

export default App;