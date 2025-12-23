import { render, screen } from '@testing-library/react';
import AttendanceTable from '../components/AttendanceTable';

test('renders attendance records in table', () => {
  const records = [
    { participant: 'John Doe', activity: 'Training', checkInTime: '2025-12-18', method: 'QR' }
  ];
  render(<AttendanceTable records={records} />);

  expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
  expect(screen.getByText(/Training/i)).toBeInTheDocument();
});
