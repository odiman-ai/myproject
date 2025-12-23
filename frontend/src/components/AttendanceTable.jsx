import React from 'react';

const AttendanceTable = ({ records }) => (
  <table>
    <thead>
      <tr>
        <th>Participant</th>
        <th>Activity</th>
        <th>Check-In</th>
        <th>Method</th>
      </tr>
    </thead>
    <tbody>
      {records.map((r, i) => (
        <tr key={i}>
          <td>{r.participant}</td>
          <td>{r.activity}</td>
          <td>{r.checkInTime}</td>
          <td>{r.method}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

export default AttendanceTable;
