import { render, screen, fireEvent } from '@testing-library/react';
import SurveyForm from '../components/SurveyForm';

test('renders survey questions and submits answers', () => {
  const mockSubmit = jest.fn();
  const questions = ['Age?', 'Gender?'];
  render(<SurveyForm questions={questions} onSubmit={mockSubmit} />);

  fireEvent.change(screen.getByLabelText(/Age?/i), { target: { value: '30' } });
  fireEvent.change(screen.getByLabelText(/Gender?/i), { target: { value: 'Male' } });
  fireEvent.click(screen.getByText(/Submit Survey/i));

  expect(mockSubmit).toHaveBeenCalledWith({ 'Age?': '30', 'Gender?': 'Male' });
});
