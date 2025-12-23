import reducer, { addBeneficiary, removeBeneficiary } from '../store/beneficiarySlice';

test('adds and removes beneficiary', () => {
  const initialState = [];
  const beneficiary = { id: 'B001', name: 'John Doe' };

  let state = reducer(initialState, addBeneficiary(beneficiary));
  expect(state.length).toBe(1);

  state = reducer(state, removeBeneficiary('B001'));
  expect(state.length).toBe(0);
});
