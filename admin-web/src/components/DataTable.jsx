export default function DataTable({ columns, rows, empty = "Nenhum registro encontrado." }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows?.length ? (
            rows.map((row, index) => (
              <tr key={row.id || index}>
                {columns.map((column) => (
                  <td key={column.key} data-label={column.label}>
                    {column.render ? column.render(row) : row[column.key] || "-"}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td className="empty-cell" colSpan={columns.length}>{empty}</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
