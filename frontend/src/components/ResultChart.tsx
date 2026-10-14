import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";

import type { AnalysisResponse } from "../types/analysis";

interface ResultChartProps {
  rows: Record<string, unknown>[];
  chart: NonNullable<AnalysisResponse["chart"]>;
}

const ResultChart = ({rows, chart}: ResultChartProps) => {
  if(rows.length === 0){
    return null;
  }

  const data = rows.map((row) => {
  const normalized = { ...row };

  for(const key of [chart.x, chart.y]){
    const value = normalized[key];

    if(typeof value === "string" && value.trim() !== "" && Number.isFinite(Number(value))){
      normalized[key] = Number(value);
    }
  }

  return normalized;
});

  return(
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-6 text-lg font-semibold text-gray-900">
        {chart.title}
      </h2>

      <div className="h-96 w-full">
        <ResponsiveContainer width="100%" height="100%">
          
          {chart.type === "bar" ? (
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3"/>

              <XAxis dataKey={chart.x}/>
              <YAxis/>
              <Tooltip/>

              <Bar dataKey={chart.y}/>
            </BarChart>
          
        ) : chart.type === "line" ? (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3"/>

              <XAxis dataKey={chart.x}/>
              <YAxis/>
              <Tooltip/>
              <Line type="monotone" dataKey={chart.y}/>
            </LineChart>
            
          ) : chart.type === "scatter" ? (
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3"/>

              <XAxis type="number" dataKey={chart.x}/>
              <YAxis type="number" dataKey={chart.y}/>
              <Tooltip/>

              <Scatter data={data}/>
            </ScatterChart>
          ) : null}
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default ResultChart;