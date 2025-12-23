import { createSlice } from '@reduxjs/toolkit';

const beneficiarySlice = createSlice({
  name: 'beneficiaries',
  initialState: [],
  reducers: {
    addBeneficiary: (state, action) => {
      state.push(action.payload);
    },
    removeBeneficiary: (state, action) => {
      return state.filter(b => b.id !== action.payload);
    }
  }
});

export const { addBeneficiary, removeBeneficiary } = beneficiarySlice.actions;
export default beneficiarySlice.reducer;
