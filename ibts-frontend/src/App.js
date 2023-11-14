import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MyComponent from './MyComponent';
import QuestionAnswers from './QuestionAnswers'; // Import your new component

const App = () => {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Define your routes here */}
          <Route path="/questionanswers" element={<QuestionAnswers />} />
          <Route path="/" element={<MyComponent />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
