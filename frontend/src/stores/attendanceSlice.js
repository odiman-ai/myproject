import { createSlice } from '@reduxjs/toolkit';

const attendanceSlice = createSlice({
  name: 'attendance',
  initialState: [],
  reducers: {
    addRecord: (state, action) => {
      state.push(action.payload);
    },
    clearRecords: () => {
      return [];
    }
  }
});

export const { addRecord, clearRecords } = attendanceSlice.actions;
export default attendanceSlice.reducer;
