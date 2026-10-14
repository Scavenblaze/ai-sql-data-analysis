interface ResultTableProps {
  rows: Record<string, unknown>[];
}

const ResultTable = ({rows}: ResultTableProps) => {
  if(rows.length === 0){
    return(
      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <p className="text-gray-500">
          No results found.
        </p>
      </div>
    );
  }

  const columns = Object.keys(rows[0]);

  return(
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-6 py-3 font-semibold text-gray-700">
                  {column}
                </th>
              ))}
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-200">
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {columns.map((column) => (
                  <td key={column} className="whitespace-nowrap px-6 py-3 text-gray-700">
                    {String(row[column] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ResultTable;