from marshmallow import Schema, fields, validate

# Request Schemas
class LoginRequestSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=1))

class RefreshTokenRequestSchema(Schema):
    refresh_token = fields.Str(required=True)

class LogoutRequestSchema(Schema):
    refresh_token = fields.Str(required=True)

class ValidateTokenRequestSchema(Schema):
    token = fields.Str(required=True)

class RegisterRequestSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=20))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    firstName = fields.Str(load_default="")
    lastName = fields.Str(load_default="")

class OAuthCallbackRequestSchema(Schema):
    code = fields.Str(required=True)

# Response Schemas
class ErrorResponseSchema(Schema):
    error = fields.Str()
    details = fields.Raw(load_default=None)

class LoginResponseSchema(Schema):
    message = fields.Str()
    access_token = fields.Str()
    refresh_token = fields.Str()
    expires_in = fields.Int()
    refresh_expires_in = fields.Int()
    token_type = fields.Str()
    user_info = fields.Dict()

class RefreshTokenResponseSchema(Schema):
    message = fields.Str()
    access_token = fields.Str()
    refresh_token = fields.Str()
    expires_in = fields.Int()
    refresh_expires_in = fields.Int()
    token_type = fields.Str()

class LogoutResponseSchema(Schema):
    message = fields.Str()

class ValidateTokenResponseSchema(Schema):
    valid = fields.Bool()
    claims = fields.Dict(load_default=None)

class UserInfoResponseSchema(Schema):
    user_info = fields.Dict()

class RegisterResponseSchema(Schema):
    message = fields.Str()
    username = fields.Str()
    email = fields.Str()

class SSOProviderSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    displayName = fields.Str()

class SSOProvidersResponseSchema(Schema):
    providers = fields.List(fields.Nested(SSOProviderSchema))

class SSOLoginResponseSchema(Schema):
    redirect_url = fields.Str()

class OAuthCallbackResponseSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
    expires_in = fields.Int()

class PublicResponseSchema(Schema):
    message = fields.Str()
    data = fields.Str()

class ProtectedResponseSchema(Schema):
    message = fields.Str()
    authenticated_user = fields.Str()
    user_id = fields.Str()
    roles = fields.List(fields.Str())

class AdminResponseSchema(Schema):
    message = fields.Str()
    admin_user = fields.Str()
    admin_actions = fields.List(fields.Str())

class UserDataResponseSchema(Schema):
    message = fields.Str()
    user = fields.Dict()

class HealthResponseSchema(Schema):
    status = fields.Str()
    service = fields.Str()