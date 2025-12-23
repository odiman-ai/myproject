import { render, screen } from '@testing-library/react';
import Programs from '../pages/Programs';

test('renders list of programs', () => {
  const programs = [{ id: 'P001', name: 'Nutrition Program' }];
  render(<Programs programs={programs} />);
  expect(screen.getByText(/Nutrition Program/i)).toBeInTheDocument();
});
