import { render, screen } from '@testing-library/react';
import BeneficiaryCard from '../components/BeneficiaryCard';

test('renders beneficiary details', () => {
  const beneficiary = {
    id: 'B001',
    fullName: 'Jane Doe',
    participantCode: 'PC001',
    status: 'Active',
    phoneNumber: '1234567890'
  };
  render(<BeneficiaryCard beneficiary={beneficiary} />);

  expect(screen.getByText(/Jane Doe/i)).toBeInTheDocument();
  expect(screen.getByText(/PC001/i)).toBeInTheDocument();
  expect(screen.getByText(/Active/i)).toBeInTheDocument();
});
