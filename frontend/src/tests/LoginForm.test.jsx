import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from '../components/LoginForm';

test('renders login form and submits credentials', () => {
  const mockLogin = jest.fn();
  render(<LoginForm onLogin={mockLogin} />);

  fireEvent.change(screen.getByPlaceholderText(/Email/i), { target: { value: 'test@example.com' } });
  fireEvent.change(screen.getByPlaceholderText(/Password/i), { target: { value: 'password123' } });
  fireEvent.click(screen.getByText(/Login/i));

  expect(mockLogin).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password123' });
});
