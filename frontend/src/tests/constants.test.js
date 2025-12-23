import { API_BASE_URL, APP_NAME } from '../utils/constants';

test('constants are defined', () => {
  expect(API_BASE_URL).toBe('https://api.ngo-system.org');
  expect(APP_NAME).toBe('Beneficiary Management System');
});
