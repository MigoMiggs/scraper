import React, { useState } from 'react';
import axios from 'axios';

const QuestionAnswers = () => {
  const [question, setQuestion] = useState('');
  const [answers, setAnswers] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null); // New state for error handling

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null); // Reset error state on new submission
    try {
      const res = await axios.get('http://localhost:5000/question_answer', {
        params: { question, answers, kb: 'chroma_clean_ada', llm: 'gpt-3.5-turbo' }
      });
      setResponse(res.data);
    } catch (err) {
      console.error('Error fetching data: ', err);
      setError('Error fetching data'); // Set error message
      setResponse(null); // Reset response on error
    } finally {
      setLoading(false); // Ensure loading is set to false in both success and error cases
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
      {loading && <div className="loading-spinner"></div>}
      {error && <div className="error-message">{error}</div>}
      {response && (
        <div className="answer-container">
          <h2>Answer:</h2>
          <p>{JSON.stringify(response)}</p>
        </div>
      )}
    </div>
  );
};

export default QuestionAnswers;
