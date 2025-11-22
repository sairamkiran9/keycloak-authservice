/**
 * Frontend validation utilities for registration
 * Mirrors backend validation for better UX
 */

export const validateUsername = (username) => {
  if (!username) {
    return { valid: false, error: 'Username is required' };
  }

  if (username.length < 3) {
    return { valid: false, error: 'Username must be at least 3 characters' };
  }

  if (username.length > 20) {
    return { valid: false, error: 'Username must be no more than 20 characters' };
  }

  // Must start with letter or number, then alphanumeric, underscore, dash
  const usernamePattern = /^[a-zA-Z0-9][a-zA-Z0-9_-]*$/;
  if (!usernamePattern.test(username)) {
    return {
      valid: false,
      error: 'Username must start with a letter or number and contain only letters, numbers, underscores, and dashes'
    };
  }

  return { valid: true };
};

export const validateEmail = (email) => {
  if (!email) {
    return { valid: false, error: 'Email is required' };
  }

  // Basic RFC 5322 compliant email pattern
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailPattern.test(email)) {
    return { valid: false, error: 'Invalid email format' };
  }

  if (email.length > 255) {
    return { valid: false, error: 'Email is too long' };
  }

  return { valid: true };
};

export const validatePasswordStrength = (password, minLength = 8) => {
  if (!password) {
    return { valid: false, error: 'Password is required', strength: 'none' };
  }

  if (password.length < minLength) {
    return {
      valid: false,
      error: `Password must be at least ${minLength} characters`,
      strength: 'weak'
    };
  }

  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasDigit = /\d/.test(password);

  if (!hasUpper) {
    return {
      valid: false,
      error: 'Password must contain at least one uppercase letter',
      strength: 'weak'
    };
  }

  if (!hasLower) {
    return {
      valid: false,
      error: 'Password must contain at least one lowercase letter',
      strength: 'weak'
    };
  }

  if (!hasDigit) {
    return {
      valid: false,
      error: 'Password must contain at least one number',
      strength: 'weak'
    };
  }

  // Determine strength
  let strength = 'medium';
  if (password.length >= 12 && /[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    strength = 'strong';
  }

  return { valid: true, strength };
};

export const getPasswordStrengthColor = (strength) => {
  const colors = {
    none: '#ddd',
    weak: '#ff4444',
    medium: '#ffaa00',
    strong: '#00C851'
  };
  return colors[strength] || colors.none;
};

export const validateName = (name, fieldName = 'Name') => {
  if (!name) {
    // Names are optional
    return { valid: true };
  }

  if (name.length > 50) {
    return { valid: false, error: `${fieldName} must be no more than 50 characters` };
  }

  // Allow letters, spaces, hyphens, apostrophes
  const namePattern = /^[a-zA-Z\s'-]+$/;
  if (!namePattern.test(name)) {
    return {
      valid: false,
      error: `${fieldName} can only contain letters, spaces, hyphens, and apostrophes`
    };
  }

  return { valid: true };
};