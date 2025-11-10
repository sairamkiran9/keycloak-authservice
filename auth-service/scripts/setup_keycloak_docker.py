#!/usr/bin/env python3
"""
Keycloak Docker Automation Script
Automates Keycloak setup for Docker Compose deployment with predefined client secret
"""

import sys
import os
import time
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError, KeycloakPostError


class KeycloakDockerSetup:
    def __init__(self):
        """Initialize Keycloak Admin connection with environment variables"""
        self.server_url = os.getenv('KEYCLOAK_SERVER_URL', 'http://keycloak:8080')
        self.admin_username = os.getenv('KEYCLOAK_ADMIN', 'admin')
        self.admin_password = os.getenv('KEYCLOAK_ADMIN_PASSWORD', 'admin')
        self.realm_name = os.getenv('KEYCLOAK_REALM', 'microservices-realm')
        self.client_id = os.getenv('KEYCLOAK_CLIENT_ID', 'auth-service')
        self.client_secret = os.getenv('KEYCLOAK_CLIENT_SECRET')

        if not self.client_secret:
            print("❌ ERROR: KEYCLOAK_CLIENT_SECRET environment variable is required")
            sys.exit(1)

        print(f"🔗 Connecting to Keycloak at {self.server_url}...")
        print(f"   Realm: {self.realm_name}")
        print(f"   Client: {self.client_id}")

        # Wait for Keycloak to be fully ready
        max_retries = 30
        retry_delay = 5

        print(f"⏳ Waiting for Keycloak to be ready (max {max_retries * retry_delay}s)...")

        for attempt in range(1, max_retries + 1):
            try:
                # Try to connect and verify Keycloak is responding
                test_admin = KeycloakAdmin(
                    server_url=self.server_url,
                    username=self.admin_username,
                    password=self.admin_password,
                    realm_name='master',
                    verify=True
                )
                # Try to get master realm to verify API is working
                test_admin.get_realm('master')

                # If we get here, Keycloak is ready
                self.keycloak_admin = test_admin
                print("✅ Keycloak is ready and responding!\n")
                break
            except Exception as e:
                if attempt < max_retries:
                    print(f"⏳ Attempt {attempt}/{max_retries} - Waiting for Keycloak... (retrying in {retry_delay}s)")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Failed to connect to Keycloak after {max_retries} attempts")
                    print(f"   Error: {str(e)}")
                    raise

    def create_realm(self):
        """Create realm if it doesn't exist"""
        print(f"📦 Creating realm: {self.realm_name}")

        try:
            # Check if realm exists
            self.keycloak_admin.get_realm(self.realm_name)
            print(f"✓ Realm '{self.realm_name}' already exists\n")
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

    def create_client_with_secret(self):
        """Create confidential client with predefined secret"""
        print(f"🔑 Creating client: {self.client_id}")

        # Switch to the target realm
        self.keycloak_admin.realm_name = self.realm_name

        try:
            # Check if client exists
            try:
                client_id_internal = self.keycloak_admin.get_client_id(self.client_id)
            except KeycloakGetError:
                client_id_internal = None

            if client_id_internal:
                print(f"✓ Client '{self.client_id}' already exists")

                # Update the client secret to match the predefined one
                client_update = {"secret": self.client_secret}
                self.keycloak_admin.update_client(client_id_internal, payload=client_update)
                print(f"✅ Client secret updated to predefined value\n")

                # Configure service account permissions for user management
                self.assign_client_roles(client_id_internal)
                return
        except KeycloakGetError:
            pass

        # Create client WITHOUT secret (Keycloak will auto-generate)
        client_payload = {
            "clientId": self.client_id,
            "name": "Auth Service Client",
            "description": "Python Flask Authentication Service (Docker)",
            "enabled": True,
            "protocol": "openid-connect",
            "publicClient": False,
            "serviceAccountsEnabled": True,
            "directAccessGrantsEnabled": True,
            "standardFlowEnabled": True,
            "implicitFlowEnabled": False,
            "redirectUris": [
                "http://localhost:5000/*",
                "http://localhost:3000/*",
                "http://auth-service:5000/*",
                "http://frontend:3000/*"
            ],
            "webOrigins": ["*"],
            "attributes": {
                "access.token.lifespan": "900",
            }
        }

        client_id_internal = self.keycloak_admin.create_client(payload=client_payload)
        print(f"✅ Client '{self.client_id}' created")

        # Now set the predefined secret by updating the client
        client_update = {
            "secret": self.client_secret
        }
        self.keycloak_admin.update_client(client_id_internal, payload=client_update)
        print(f"✅ Client secret set to predefined value\n")

        # Configure service account permissions for user management
        self.assign_client_roles(client_id_internal)

    def assign_client_roles(self, client_id_internal: str):
        """
        Assign necessary roles to service account for user management

        Args:
            client_id_internal: Internal Keycloak client ID
        """
        print("🔐 Configuring service account permissions")

        try:
            # Get service account user
            service_account_user = self.keycloak_admin.get_client_service_account_user(client_id_internal)

            if not service_account_user:
                print("⚠️  Warning: Service account not found")
                return

            service_account_user_id = service_account_user['id']

            # Get realm-management client
            try:
                realm_mgmt_client_id = self.keycloak_admin.get_client_id('realm-management')
            except KeycloakGetError:
                print("⚠️  Warning: realm-management client not found")
                return

            if not realm_mgmt_client_id:
                print("⚠️  Warning: realm-management client ID is None")
                return

            # Get required roles
            available_roles = self.keycloak_admin.get_client_roles(realm_mgmt_client_id)

            roles_to_assign = []
            required_role_names = ['manage-users', 'view-users', 'query-users']

            for role_name in required_role_names:
                role = next((r for r in available_roles if r['name'] == role_name), None)
                if role:
                    roles_to_assign.append(role)

            if roles_to_assign:
                # Assign client roles to service account
                self.keycloak_admin.assign_client_role(
                    client_id=realm_mgmt_client_id,
                    user_id=service_account_user_id,
                    roles=roles_to_assign
                )
                print(f"✅ Assigned roles {[r['name'] for r in roles_to_assign]} to service account")
            else:
                print("⚠️  Warning: Required roles not found")

        except Exception as e:
            print(f"⚠️  Warning: Could not assign service account roles: {str(e)}")
            print("   You may need to manually assign 'manage-users' role in Keycloak admin console")

    def create_roles(self):
        """Create realm roles"""
        print("👥 Creating realm roles")

        self.keycloak_admin.realm_name = self.realm_name

        roles = ['user', 'admin', 'service']

        for role_name in roles:
            try:
                # Check if role exists
                self.keycloak_admin.get_realm_role(role_name)
                print(f"✓ Role '{role_name}' already exists")
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
                print(f"✓ User '{username}' already exists")
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
                # Get current user roles to avoid duplicate assignment
                current_roles = self.keycloak_admin.get_realm_roles_of_user(user_id)
                current_role_names = [role['name'] for role in current_roles]

                # Only assign roles that aren't already assigned
                new_roles = [role for role in roles_to_assign if role['name'] not in current_role_names]

                if new_roles:
                    self.keycloak_admin.assign_realm_roles(user_id=user_id, roles=new_roles)
                    print(f"✅ Assigned roles {[r['name'] for r in new_roles]} to '{username}'")
                else:
                    print(f"✓ Roles already assigned to '{username}'")

        except Exception as e:
            print(f"❌ Error creating user '{username}': {str(e)}")

        print()

    def setup_all(self):
        """Run complete Keycloak setup"""
        print("=" * 60)
        print("🚀 KEYCLOAK DOCKER AUTOMATED SETUP")
        print("=" * 60)
        print()

        try:
            # 1. Create realm
            self.create_realm()

            # 2. Create client with predefined secret
            self.create_client_with_secret()

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

            print("=" * 60)
            print("✅ KEYCLOAK DOCKER SETUP COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print()
            print("📝 Configuration Summary:")
            print(f"   Keycloak URL: {self.server_url}")
            print(f"   Realm: {self.realm_name}")
            print(f"   Client ID: {self.client_id}")
            print(f"   Client Secret: {self.client_secret[:8]}... (configured)")
            print()
            print("🔑 Test Users:")
            print("   testuser / password123 (role: user)")
            print("   adminuser / admin123 (roles: user, admin)")
            print()
            print("✅ All services can now start successfully!")
            print()

        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    try:
        setup = KeycloakDockerSetup()
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
