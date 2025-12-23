import React, { useState } from 'react';

const SurveyForm = ({ questions, onSubmit }) => {
  const [answers, setAnswers] = useState({});

  const handleChange = (q, value) => {
    setAnswers({ ...answers, [q]: value });
  };

  const handleSubmit = e => {
    e.preventDefault();
    onSubmit(answers);
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Survey</h2>
      {questions.map((q, i) => (
        <div key={i}>
          <label>{q}</label>
          <input type="text" onChange={e => handleChange(q, e.target.value)} />
        </div>
      ))}
      <button type="submit">Submit Survey</button>
    </form>
  );
};

export default SurveyForm;
