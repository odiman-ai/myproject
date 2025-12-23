import React from 'react';

const BeneficiaryCard = ({ beneficiary }) => (
  <div className="card">
    <h3>{beneficiary.fullName}</h3>
    <p>Code: {beneficiary.participantCode}</p>
    <p>Status: {beneficiary.status}</p>
    <p>Phone: {beneficiary.phoneNumber}</p>
  </div>
);

export default BeneficiaryCard;
