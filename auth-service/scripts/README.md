# Keycloak Automation Scripts

This directory contains automation scripts for setting up and managing Keycloak.

## Scripts

### `setup_keycloak.py`

Automated setup script that configures Keycloak with all necessary components.

**What it does:**
- ✅ Creates the `microservices-realm` realm
- ✅ Configures token lifespan settings
- ✅ Creates the `auth-service` confidential client
- ✅ Generates and displays client secret
- ✅ Creates realm roles: `user`, `admin`, `service`
- ✅ Creates test users:
  - `testuser` / `password123` (role: user)
  - `adminuser` / `admin123` (roles: user, admin)

**Usage:**

```bash
# Make sure Keycloak is running
docker-compose up -d

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Run the setup script
python scripts/setup_keycloak.py
```

**Environment Variables:**

The script uses the following environment variables (with defaults):

| Variable | Default | Description |
|----------|---------|-------------|
| `KEYCLOAK_ADMIN_USER` | `admin` | Keycloak admin username |
| `KEYCLOAK_ADMIN_PASSWORD` | `admin` | Keycloak admin password |
| `KEYCLOAK_SERVER_URL` | from `.env` | Keycloak server URL |
| `KEYCLOAK_REALM` | from `.env` | Target realm name |
| `KEYCLOAK_CLIENT_ID` | from `.env` | Client ID to create |

**Output:**

The script will:
1. Display progress for each step
2. Show the client secret (save this!)
3. Indicate if components already exist
4. Provide next steps and testing commands

**Example Output:**

```
============================================================
🚀 KEYCLOAK AUTOMATED SETUP
============================================================

🔗 Connecting to Keycloak at http://localhost:8080...
✅ Connected to Keycloak successfully

📦 Creating realm: microservices-realm
✅ Realm 'microservices-realm' created successfully

🔑 Creating client: auth-service
✅ Client 'auth-service' created successfully
🔐 Client Secret: gcSBjlz893TkOXRRA7CDtdsCEtmYdGq3
💡 Update your .env file with: KEYCLOAK_CLIENT_SECRET=gcSBjlz893TkOXRRA7CDtdsCEtmYdGq3

👥 Creating realm roles
✅ Role 'user' created
✅ Role 'admin' created
✅ Role 'service' created

👥 Creating test users
------------------------------------------------------------
👤 Creating user: testuser
✅ User 'testuser' created
✅ Assigned roles ['user'] to 'testuser'

👤 Creating user: adminuser
✅ User 'adminuser' created
✅ Assigned roles ['user', 'admin'] to 'adminuser'

============================================================
✅ KEYCLOAK SETUP COMPLETED SUCCESSFULLY!
============================================================
```

## Advanced Usage

### Custom User Creation

You can modify the script to add more users. Edit the `setup_all()` method:

```python
self.create_user(
    username='newuser',
    email='new@example.com',
    password='securepass',
    first_name='New',
    last_name='User',
    roles=['user']
)
```

### Reset Everything

To reset and re-run the setup:

```bash
# Stop Keycloak and remove volumes
docker-compose down -v

# Start Keycloak fresh
docker-compose up -d

# Wait 20-30 seconds for startup

# Run setup script again
python scripts/setup_keycloak.py
```

### Integration with CI/CD

Add to your CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Setup Keycloak
  run: |
    docker-compose up -d
    sleep 30
    source venv/bin/activate
    python scripts/setup_keycloak.py
```

## Troubleshooting

**Connection Error:**
```
Error: Cannot connect to Keycloak
```
- Ensure Keycloak is running: `docker ps | grep keycloak`
- Check Keycloak logs: `docker-compose logs keycloak`
- Wait for Keycloak to fully start (20-30 seconds)

**Authentication Error:**
```
Error: Invalid admin credentials
```
- Check `KEYCLOAK_ADMIN_USER` and `KEYCLOAK_ADMIN_PASSWORD`
- Default is `admin` / `admin`

**Realm Already Exists:**
```
ℹ️  Realm 'microservices-realm' already exists
```
- This is normal - script is idempotent
- Existing components won't be recreated

## Dependencies

The script uses the `python-keycloak` library, which is already included in `requirements.txt`:

```txt
python-keycloak==3.7.0
```

## Security Notes

⚠️ **Important for Production:**

1. **Change default passwords** - Don't use `password123` or `admin123` in production
2. **Store client secret securely** - Use secrets management (e.g., AWS Secrets Manager, HashiCorp Vault)
3. **Don't commit secrets** - `.env` is in `.gitignore`
4. **Use HTTPS** - Always use HTTPS in production
5. **Rotate credentials** - Regularly rotate client secrets and user passwords

## Additional Resources

- [Keycloak Admin REST API](https://www.keycloak.org/docs-api/latest/rest-api/)
- [python-keycloak Documentation](https://python-keycloak.readthedocs.io/)
- [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
