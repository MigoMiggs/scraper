import React, { useState } from 'react';
import axios from 'axios';

const MyComponent = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false); // New loading state

  
  // lock the size of the answer section
  const createMarkup = (text) => {  

    return {__html: text.replace(/\n/g, '<br />')};
  }
  
  const fetchAnswer = async () => {
    setLoading(true); // Set loading to true when starting to fetch
    try {
      const response = await axios.get('http://localhost:5000/question', {
        params: {
          question: question,
          kb: 'chroma',
          llm: 'gpt-3.5-turbo',
        },
      });
      setAnswer(response.data.answer);
    } catch (error) {
      console.error('There was an error fetching the answer!', error);
    } finally {
      setLoading(false); // Set loading to false once fetching is complete
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchAnswer();
  };
  
  return (
    <div>
      <h1>Question Fetcher</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Question: 
          <input 
            type="text" 
            value={question} 
            onChange={(e) => setQuestion(e.target.value)} 
          />
        </label>
        <button type="submit" disabled={loading}>Fetch Answer</button>
      </form>
      {loading ? (
        <div className="loading-spinner">spinnnnnnn</div>
      ) : (
        answer && (
          // the div below should be fixed size 
          // and should not change when the answer changes
          <div className="answer-container">
            <h2>Answer:</h2>
            <p dangerouslySetInnerHTML={createMarkup(answer)} />
          </div>
        )
      )}
    </div>
  );
};

export default MyComponent;
