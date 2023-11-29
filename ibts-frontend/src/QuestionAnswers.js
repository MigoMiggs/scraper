import React, { useState } from 'react';
import axios from 'axios';

const QuestionAnswers = () => {
  const [question, setQuestion] = useState('');
  const [answers, setAnswers] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false); // New loading state

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
        setLoading(true);
      const res = await axios.get('http://localhost:5000/question_answer', {
        params: { question, answers, kb: 'chroma_clean_ada', llm: 'gpt-3.5-turbo' }
      });
      alert('Success!')
      setResponse(res.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data: ', error);
    }
  };

  return (
    <div>
      <h1>Question and Answers</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Question:</label>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </div>
        <div>
          <label>Answers:</label>
          <p></p>
          <textarea
            value={answers}
            onChange={(e) => setAnswers(e.target.value)}
          />
        </div>
        <button type="submit">Submit</button>
      </form>
      {loading ? (
        <div className="loading-spinner"></div>
      ) : (
        response && (
          // the div below should be fixed size 
          // and should not change when the answer changes
          <div className="answer-container">
            <h2>Answer:</h2>
            <p>{JSON.stringify(response)}</p>
          </div>
        )
      )}
    </div>
  );
};

export default QuestionAnswers;
