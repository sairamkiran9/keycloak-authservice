from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError, KeycloakPostError
from app.config import Config


class KeycloakAdminClient:
    def __init__(self):
        """Initialize Keycloak Admin client"""
        self.admin = KeycloakAdmin(
            server_url=Config.KEYCLOAK_SERVER_URL,
            username=Config.KEYCLOAK_ADMIN,
            password=Config.KEYCLOAK_ADMIN_PASSWORD,
            realm_name=Config.KEYCLOAK_REALM,
            verify=True
        )

    def check_user_exists(self, username: str = None, email: str = None) -> dict:
        """
        Check if user with username or email already exists

        Args:
            username: Username to check
            email: Email to check

        Returns:
            {
                'exists': True/False,
                'field': 'username' or 'email',
                'message': 'Error message if exists'
            }
        """
        try:
            # Check username
            if username:
                users = self.admin.get_users({"username": username})
                if users:
                    return {
                        'exists': True,
                        'field': 'username',
                        'message': 'Username already exists'
                    }

            # Check email
            if email:
                users = self.admin.get_users({"email": email})
                if users:
                    return {
                        'exists': True,
                        'field': 'email',
                        'message': 'Email already registered'
                    }

            return {'exists': False}

        except Exception as e:
            return {
                'exists': False,
                'error': f'Error checking user: {str(e)}'
            }

    def create_user(self, username: str, email: str, password: str,
                    first_name: str = '', last_name: str = '') -> dict:
        """
        Create new user in Keycloak

        Args:
            username: Unique username
            email: User email
            password: User password
            first_name: Optional first name
            last_name: Optional last name

        Returns:
            {
                'success': True/False,
                'user_id': 'keycloak-user-id' (if success),
                'error': 'error message' (if failure)
            }
        """
        try:
            user_payload = {
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "emailVerified": False,  # Set to False since we skip verification
                "credentials": [{
                    "type": "password",
                    "value": password,
                    "temporary": False  # User doesn't need to change password on first login
                }]
            }

            # Create user
            user_id = self.admin.create_user(payload=user_payload)

            return {
                'success': True,
                'user_id': user_id
            }

        except KeycloakPostError as e:
            return {
                'success': False,
                'error': f'Failed to create user: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def assign_default_role(self, user_id: str) -> dict:
        """
        Assign default 'user' role to newly registered user

        Args:
            user_id: Keycloak user ID

        Returns:
            {'success': True/False, 'error': 'message' (if failure)}
        """
        try:
            # Get the 'user' role
            available_roles = self.admin.get_realm_roles()
            user_role = next((role for role in available_roles if role['name'] == 'user'), None)

            if not user_role:
                return {
                    'success': False,
                    'error': 'Default user role not found in Keycloak'
                }

            # Assign role to user
            self.admin.assign_realm_roles(user_id=user_id, roles=[user_role])

            return {'success': True}

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to assign role: {str(e)}'
            }

    def register_user(self, username: str, email: str, password: str,
                     first_name: str = '', last_name: str = '') -> dict:
        """
        Complete registration flow: check existence, create user, assign role

        Returns:
            {
                'success': True/False,
                'user_id': 'id' (if success),
                'username': 'username' (if success),
                'email': 'email' (if success),
                'error': 'message' (if failure)
            }
        """
        # Check if user already exists
        exists = self.check_user_exists(username=username, email=email)
        if exists['exists']:
            return {
                'success': False,
                'error': exists['message'],
                'field': exists['field']
            }

        # Create user
        result = self.create_user(username, email, password, first_name, last_name)
        if not result['success']:
            return result

        user_id = result['user_id']

        # Assign default role
        role_result = self.assign_default_role(user_id)
        if not role_result['success']:
            # User created but role assignment failed - log warning
            print(f"Warning: User {username} created but role assignment failed: {role_result['error']}")

        return {
            'success': True,
            'user_id': user_id,
            'username': username,
            'email': email
        }