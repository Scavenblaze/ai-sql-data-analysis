export interface AnalysisRequest{
  question: string;
}

export interface ChartSpec{
  type: "bar" | "line" | "scatter";
  x: string;
  y: string;
  title: string;
}

export interface AnalysisResponse{
  question: string;
  answer: string;
  sql: string;
  rows: Record<string, unknown>[];
  row_count: number;
  chart: ChartSpec | null;
}