import type { AnalysisRequest, AnalysisResponse } from "../types/analysis";

const API_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_URL){
  throw new Error("VITE_API_BASE_URL is not configured");
}

export const analyzeQuestion = async(question: string, signal?: AbortSignal) : Promise<AnalysisResponse> =>{
  const request: AnalysisRequest = { question };

  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
    signal,
  });

  if(!response.ok){
    const error = await response.json();
    throw new Error(error.detail || "Failed to analyze question");
  }

  return response.json();
}