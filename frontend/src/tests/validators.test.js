import { validateEmail, validatePhone } from '../utils/validators';

test('validates email correctly', () => {
  expect(validateEmail('test@example.com')).toBe(true);
  expect(validateEmail('invalid')).toBe(false);
});

test('validates phone correctly', () => {
  expect(validatePhone('1234567890')).toBe(true);
  expect(validatePhone('123')).toBe(false);
});
