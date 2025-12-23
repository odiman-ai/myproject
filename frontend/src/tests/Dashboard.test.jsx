import { render, screen } from '@testing-library/react';
import Dashboard from '../pages/Dashboard';

test('renders dashboard welcome message', () => {
  render(<Dashboard />);
  expect(screen.getByText(/Welcome to the Beneficiary Management System/i)).toBeInTheDocument();
});
