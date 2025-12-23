import React from 'react';
import BeneficiaryCard from '../components/BeneficiaryCard';

const Beneficiaries = ({ beneficiaries }) => (
  <div>
    <h1>Beneficiaries</h1>
    {beneficiaries.map(b => <BeneficiaryCard key={b.id} beneficiary={b} />)}
  </div>
);

export default Beneficiaries;
