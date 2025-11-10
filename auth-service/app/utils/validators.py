import re
from typing import Dict, Any


def validate_username(username: str) -> Dict[str, Any]:
    """
    Validate username format

    Rules:
    - 3-20 characters
    - Alphanumeric, underscore, and dash only
    - Must start with a letter or number

    Returns:
        {'valid': True/False, 'error': 'error message'}
    """
    if not username:
        return {'valid': False, 'error': 'Username is required'}

    if len(username) < 3:
        return {'valid': False, 'error': 'Username must be at least 3 characters'}

    if len(username) > 20:
        return {'valid': False, 'error': 'Username must be no more than 20 characters'}

    # Must start with letter or number, then alphanumeric, underscore, dash
    username_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$'
    if not re.match(username_pattern, username):
        return {
            'valid': False,
            'error': 'Username must start with a letter or number and contain only letters, numbers, underscores, and dashes'
        }

    return {'valid': True}


def validate_email(email: str) -> Dict[str, Any]:
    """
    Validate email format using RFC 5322 compliant regex

    Returns:
        {'valid': True/False, 'error': 'error message'}
    """
    if not email:
        return {'valid': False, 'error': 'Email is required'}

    # Basic RFC 5322 compliant email pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return {'valid': False, 'error': 'Invalid email format'}

    if len(email) > 255:
        return {'valid': False, 'error': 'Email is too long'}

    return {'valid': True}


def validate_password_strength(password: str, min_length: int = 8) -> Dict[str, Any]:
    """
    Validate password strength

    Rules:
    - Minimum 8 characters (configurable)
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number

    Returns:
        {'valid': True/False, 'error': 'error message', 'strength': 'weak/medium/strong'}
    """
    if not password:
        return {'valid': False, 'error': 'Password is required', 'strength': 'none'}

    if len(password) < min_length:
        return {
            'valid': False,
            'error': f'Password must be at least {min_length} characters',
            'strength': 'weak'
        }

    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))

    if not has_upper:
        return {
            'valid': False,
            'error': 'Password must contain at least one uppercase letter',
            'strength': 'weak'
        }

    if not has_lower:
        return {
            'valid': False,
            'error': 'Password must contain at least one lowercase letter',
            'strength': 'weak'
        }

    if not has_digit:
        return {
            'valid': False,
            'error': 'Password must contain at least one number',
            'strength': 'weak'
        }

    # Determine strength
    strength = 'medium'
    if len(password) >= 12 and bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
        strength = 'strong'

    return {'valid': True, 'strength': strength}


def validate_name(name: str, field_name: str = 'Name') -> Dict[str, Any]:
    """
    Validate first/last name (optional fields)

    Rules:
    - 1-50 characters if provided
    - Letters, spaces, hyphens, and apostrophes only

    Returns:
        {'valid': True/False, 'error': 'error message'}
    """
    if not name:
        # Names are optional
        return {'valid': True}

    if len(name) > 50:
        return {'valid': False, 'error': f'{field_name} must be no more than 50 characters'}

    # Allow letters, spaces, hyphens, apostrophes
    name_pattern = r'^[a-zA-Z\s\'-]+$'
    if not re.match(name_pattern, name):
        return {
            'valid': False,
            'error': f'{field_name} can only contain letters, spaces, hyphens, and apostrophes'
        }

    return {'valid': True}


def sanitize_input(text: str) -> str:
    """
    Basic sanitization to prevent XSS
    - Remove HTML tags
    - Remove null bytes
    - Trim whitespace
    """
    if not text:
        return text

    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Remove null bytes
    text = text.replace('\x00', '')
    # Trim whitespace
    text = text.strip()

    return text


def validate_registration_data(data: dict, min_password_length: int = 8) -> Dict[str, Any]:
    """
    Validate complete registration data

    Returns:
        {
            'valid': True/False,
            'errors': {'field': 'error message', ...},
            'sanitized_data': {'username': '...', 'email': '...', ...}
        }
    """
    if not isinstance(data, dict):
        return {
            'valid': False,
            'errors': {'general': 'Invalid data format'},
            'sanitized_data': {}
        }

    errors = {}
    sanitized_data = {}

    # Validate and sanitize required fields
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    first_name = data.get('firstName', '').strip()
    last_name = data.get('lastName', '').strip()

    # Validate username
    username_validation = validate_username(username)
    if not username_validation['valid']:
        errors['username'] = username_validation['error']
    else:
        sanitized_data['username'] = sanitize_input(username)

    # Validate email
    email_validation = validate_email(email)
    if not email_validation['valid']:
        errors['email'] = email_validation['error']
    else:
        sanitized_data['email'] = email.lower()  # Normalize email to lowercase

    # Validate password
    password_validation = validate_password_strength(password, min_password_length)
    if not password_validation['valid']:
        errors['password'] = password_validation['error']
    else:
        sanitized_data['password'] = password

    # Validate optional fields
    if first_name:
        first_name_validation = validate_name(first_name, 'First name')
        if not first_name_validation['valid']:
            errors['firstName'] = first_name_validation['error']
        else:
            sanitized_data['firstName'] = sanitize_input(first_name)
    else:
        sanitized_data['firstName'] = ''

    if last_name:
        last_name_validation = validate_name(last_name, 'Last name')
        if not last_name_validation['valid']:
            errors['lastName'] = last_name_validation['error']
        else:
            sanitized_data['lastName'] = sanitize_input(last_name)
    else:
        sanitized_data['lastName'] = ''

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'sanitized_data': sanitized_data
    }