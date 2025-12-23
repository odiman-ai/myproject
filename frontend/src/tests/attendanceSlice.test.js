import reducer, { addRecord, clearRecords } from '../store/attendanceSlice';

test('adds and clears attendance records', () => {
  const initialState = [];
  const record = { id: 'A001', participant: 'John Doe' };

  let state = reducer(initialState, addRecord(record));
  expect(state.length).toBe(1);

  state = reducer(state, clearRecords());
  expect(state.length).toBe(0);
});
