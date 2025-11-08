#!/usr/bin/env python3
"""
Keycloak Automation Script
Automates the setup of Keycloak realm, client, roles, and users
"""

import sys
import os
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
from keycloak.exceptions import KeycloakGetError, KeycloakPostError

# Add parent directory to path to import app config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import Config


class KeycloakSetup:
    def __init__(self):
        """Initialize Keycloak Admin connection"""
        self.server_url = Config.KEYCLOAK_SERVER_URL
        self.admin_username = os.getenv('KEYCLOAK_ADMIN_USER', 'admin')
        self.admin_password = os.getenv('KEYCLOAK_ADMIN_PASSWORD', 'admin')
        self.realm_name = Config.KEYCLOAK_REALM
        self.client_id = Config.KEYCLOAK_CLIENT_ID

        print(f"🔗 Connecting to Keycloak at {self.server_url}...")

        # Connect to Keycloak admin
        self.keycloak_admin = KeycloakAdmin(
            server_url=self.server_url,
            username=self.admin_username,
            password=self.admin_password,
            realm_name='master',
            verify=True
        )

        print("✅ Connected to Keycloak successfully\n")

    def create_realm(self):
        """Create realm if it doesn't exist"""
        print(f"📦 Creating realm: {self.realm_name}")

        try:
            # Check if realm exists
            self.keycloak_admin.get_realm(self.realm_name)
            print(f"ℹ️  Realm '{self.realm_name}' already exists\n")
            return
        except KeycloakGetError:
            pass

        # Create realm
        realm_payload = {
            "realm": self.realm_name,
            "enabled": True,
            "displayName": "Microservices Realm",
            "accessTokenLifespan": 900,  # 15 minutes
            "ssoSessionIdleTimeout": 1800,  # 30 minutes
            "ssoSessionMaxLifespan": 36000,  # 10 hours
        }

        self.keycloak_admin.create_realm(payload=realm_payload)
        print(f"✅ Realm '{self.realm_name}' created successfully\n")

        # Switch to new realm
        self.keycloak_admin.realm_name = self.realm_name

    def create_client(self):
        """Create confidential client if it doesn't exist"""
        print(f"🔑 Creating client: {self.client_id}")

        # Switch to the target realm
        self.keycloak_admin.realm_name = self.realm_name

        try:
            # Check if client exists
            client_id_internal = self.keycloak_admin.get_client_id(self.client_id)
            if client_id_internal:
                client = self.keycloak_admin.get_client(client_id_internal)
                secret = self.keycloak_admin.get_client_secrets(client_id_internal)
                print(f"ℹ️  Client '{self.client_id}' already exists")
                print(f"🔐 Client Secret: {secret['value']}")
                print(f"💡 Update your .env file with: KEYCLOAK_CLIENT_SECRET={secret['value']}\n")
                return secret['value']
        except KeycloakGetError:
            pass

        # Create client
        client_payload = {
            "clientId": self.client_id,
            "name": "Auth Service Client",
            "description": "Python Flask Authentication Service",
            "enabled": True,
            "protocol": "openid-connect",
            "publicClient": False,
            "serviceAccountsEnabled": True,
            "directAccessGrantsEnabled": True,
            "standardFlowEnabled": True,
            "implicitFlowEnabled": False,
            "redirectUris": ["http://localhost:5000/*"],
            "webOrigins": ["*"],
            "attributes": {
                "access.token.lifespan": "900",
            }
        }

        client_id_internal = self.keycloak_admin.create_client(payload=client_payload)
        print(f"✅ Client '{self.client_id}' created successfully")

        # Get client secret
        secret = self.keycloak_admin.get_client_secrets(client_id_internal)
        print(f"🔐 Client Secret: {secret['value']}")
        print(f"💡 Update your .env file with: KEYCLOAK_CLIENT_SECRET={secret['value']}\n")

        return secret['value']

    def create_roles(self):
        """Create realm roles"""
        print("👥 Creating realm roles")

        self.keycloak_admin.realm_name = self.realm_name

        roles = ['user', 'admin', 'service']

        for role_name in roles:
            try:
                # Check if role exists
                self.keycloak_admin.get_realm_role(role_name)
                print(f"ℹ️  Role '{role_name}' already exists")
            except KeycloakGetError:
                # Create role
                self.keycloak_admin.create_realm_role(
                    payload={
                        'name': role_name,
                        'description': f'{role_name.capitalize()} role'
                    }
                )
                print(f"✅ Role '{role_name}' created")

        print()

    def create_user(self, username, email, password, first_name, last_name, roles):
        """Create a user with specified roles"""
        print(f"👤 Creating user: {username}")

        self.keycloak_admin.realm_name = self.realm_name

        try:
            # Check if user exists
            users = self.keycloak_admin.get_users({"username": username})
            if users:
                print(f"ℹ️  User '{username}' already exists")
                user_id = users[0]['id']
            else:
                # Create user
                user_payload = {
                    "username": username,
                    "email": email,
                    "firstName": first_name,
                    "lastName": last_name,
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [{
                        "type": "password",
                        "value": password,
                        "temporary": False
                    }]
                }

                user_id = self.keycloak_admin.create_user(payload=user_payload)
                print(f"✅ User '{username}' created")

            # Assign roles
            available_roles = self.keycloak_admin.get_realm_roles()
            roles_to_assign = [role for role in available_roles if role['name'] in roles]

            if roles_to_assign:
                self.keycloak_admin.assign_realm_roles(user_id=user_id, roles=roles_to_assign)
                print(f"✅ Assigned roles {roles} to '{username}'")

        except Exception as e:
            print(f"❌ Error creating user '{username}': {str(e)}")

        print()

    def update_env_files(self, client_secret):
        """Update .env files with the client secret"""
        print("📝 Updating environment files with client secret")

        # Get the project root directory (3 levels up from this script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        auth_service_dir = os.path.dirname(script_dir)
        root_dir = os.path.dirname(auth_service_dir)

        # Backend .env file
        backend_env_path = os.path.join(auth_service_dir, '.env')
        frontend_env_path = os.path.join(root_dir, 'frontend', '.env')
        root_env_path = os.path.join(root_dir, '.env')

        # Update backend .env
        self._update_or_create_env(
            backend_env_path,
            {
                'SECRET_KEY': 'dev-secret-key-change-in-production',
                'DEBUG': 'True',
                'KEYCLOAK_SERVER_URL': self.server_url,
                'KEYCLOAK_REALM': self.realm_name,
                'KEYCLOAK_CLIENT_ID': self.client_id,
                'KEYCLOAK_CLIENT_SECRET': client_secret
            }
        )
        print(f"  ✅ Updated: {backend_env_path}")

        # Update frontend .env
        self._update_or_create_env(
            frontend_env_path,
            {
                'VITE_API_URL': 'http://localhost:5000'
            }
        )
        print(f"  ✅ Updated: {frontend_env_path}")

        # Update root .env (for docker-compose)
        self._update_or_create_env(
            root_env_path,
            {
                'SECRET_KEY': 'dev-secret-key-change-in-production',
                'DEBUG': 'False',
                'FLASK_ENV': 'production',
                'KEYCLOAK_REALM': self.realm_name,
                'KEYCLOAK_CLIENT_ID': self.client_id,
                'KEYCLOAK_CLIENT_SECRET': client_secret
            }
        )
        print(f"  ✅ Updated: {root_env_path}")
        print()

    def _update_or_create_env(self, file_path, variables):
        """Update or create an .env file with given variables"""
        existing_vars = {}

        # Read existing .env if it exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        existing_vars[key.strip()] = value.strip()

        # Merge with new variables (new variables take precedence)
        existing_vars.update(variables)

        # Write back to file
        with open(file_path, 'w') as f:
            f.write("# Flask Configuration\n")
            if 'SECRET_KEY' in existing_vars:
                f.write(f"SECRET_KEY={existing_vars['SECRET_KEY']}\n")
            if 'DEBUG' in existing_vars:
                f.write(f"DEBUG={existing_vars['DEBUG']}\n")
            if 'FLASK_ENV' in existing_vars:
                f.write(f"FLASK_ENV={existing_vars['FLASK_ENV']}\n")

            f.write("\n# Keycloak Configuration\n")
            if 'KEYCLOAK_SERVER_URL' in existing_vars:
                f.write(f"KEYCLOAK_SERVER_URL={existing_vars['KEYCLOAK_SERVER_URL']}\n")
            if 'KEYCLOAK_REALM' in existing_vars:
                f.write(f"KEYCLOAK_REALM={existing_vars['KEYCLOAK_REALM']}\n")
            if 'KEYCLOAK_CLIENT_ID' in existing_vars:
                f.write(f"KEYCLOAK_CLIENT_ID={existing_vars['KEYCLOAK_CLIENT_ID']}\n")
            if 'KEYCLOAK_CLIENT_SECRET' in existing_vars:
                f.write(f"KEYCLOAK_CLIENT_SECRET={existing_vars['KEYCLOAK_CLIENT_SECRET']}\n")

            # Frontend specific
            if 'VITE_API_URL' in existing_vars:
                f.write(f"VITE_API_URL={existing_vars['VITE_API_URL']}\n")

    def setup_all(self):
        """Run complete Keycloak setup"""
        print("=" * 60)
        print("🚀 KEYCLOAK AUTOMATED SETUP")
        print("=" * 60)
        print()

        try:
            # 1. Create realm
            self.create_realm()

            # 2. Create client and get secret
            client_secret = self.create_client()

            # 3. Create roles
            self.create_roles()

            # 4. Create test users
            print("👥 Creating test users")
            print("-" * 60)

            self.create_user(
                username='testuser',
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User',
                roles=['user']
            )

            self.create_user(
                username='adminuser',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                roles=['user', 'admin']
            )

            # 5. Update .env files with client secret
            if client_secret:
                self.update_env_files(client_secret)

            print("=" * 60)
            print("✅ KEYCLOAK SETUP COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print()
            print("📝 Next Steps:")
            print(f"1. Environment files have been automatically configured")
            print(f"2. Start your services (or they may already be running)")
            print(f"3. Test login: curl -X POST http://localhost:5000/auth/login \\")
            print(f"              -H 'Content-Type: application/json' \\")
            print(f"              -d '{{\"username\": \"testuser\", \"password\": \"password123\"}}'")
            print()
            print("🌐 Keycloak Admin Console: http://localhost:8080")
            print(f"   Realm: {self.realm_name}")
            print(f"   Admin: {self.admin_username} / {self.admin_password}")
            print()
            print("🔑 Test Users:")
            print("   testuser / password123 (role: user)")
            print("   adminuser / admin123 (roles: user, admin)")
            print()

            return client_secret

        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    try:
        setup = KeycloakSetup()
        setup.setup_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
