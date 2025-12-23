import React from 'react';

const Programs = ({ programs }) => (
  <div>
    <h1>Programs</h1>
    <ul>
      {programs.map(p => <li key={p.id}>{p.name}</li>)}
    </ul>
  </div>
);

export default Programs;
