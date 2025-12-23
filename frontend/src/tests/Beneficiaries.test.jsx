import { render, screen } from '@testing-library/react';
import Beneficiaries from '../pages/Beneficiaries';

test('renders list of beneficiaries', () => {
  const beneficiaries = [{ id: 'B001', fullName: 'John Doe', participantCode: 'PC001', status: 'Active', phoneNumber: '1234567890' }];
  render(<Beneficiaries beneficiaries={beneficiaries} />);
  expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
});
