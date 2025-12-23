import React from 'react';

const Reports = ({ reports }) => (
  <div>
    <h1>Reports</h1>
    <ul>
      {reports.map(r => <li key={r.id}>{r.title}</li>)}
    </ul>
  </div>
);

export default Reports;
