import { render, screen } from '@testing-library/react';
import Reports from '../pages/Reports';

test('renders list of reports', () => {
  const reports = [{ id: 'R001', title: 'Monthly Report' }];
  render(<Reports reports={reports} />);
  expect(screen.getByText(/Monthly Report/i)).toBeInTheDocument();
});
