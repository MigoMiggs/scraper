import { render, screen } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});

test('renders question fetcher link', () => {
  render(<App />);
  const linkElement = screen.getByText(/question fetcher/i);
  expect(linkElement).toBeInTheDocument();
});

test('renders question and answers link', () => {
  render(<App />);
  const linkElement = screen.getByText(/question and answers/i);
  expect(linkElement).toBeInTheDocument();
});