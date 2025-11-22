from flask import request, jsonify
from flask_smorest import Blueprint
from app.utils.jwt_utils import jwt_required
from app.schemas import (
    PublicResponseSchema, ProtectedResponseSchema, AdminResponseSchema,
    UserDataResponseSchema, ErrorResponseSchema
)

protected_bp = Blueprint('protected', 'protected', url_prefix='/api', description='Protected API endpoints')

@protected_bp.route('/public', methods=['GET'])
@protected_bp.response(200, PublicResponseSchema)
def public_endpoint():
    """Public endpoint - no authentication required"""
    return jsonify({
        'message': 'This is a public endpoint',
        'data': 'Anyone can access this'
    }), 200

@protected_bp.route('/protected', methods=['GET'])
@protected_bp.doc(security=[{"bearerAuth": []}])
@protected_bp.response(200, ProtectedResponseSchema)
@protected_bp.response(401, ErrorResponseSchema)
@jwt_required()
def protected_endpoint():
    """Protected endpoint - requires valid JWT token"""
    user_claims = request.user_claims
    
    return jsonify({
        'message': 'This is a protected endpoint',
        'authenticated_user': user_claims['username'],
        'user_id': user_claims['user_id'],
        'roles': user_claims['roles']
    }), 200

@protected_bp.route('/admin', methods=['GET'])
@protected_bp.doc(security=[{"bearerAuth": []}])
@protected_bp.response(200, AdminResponseSchema)
@protected_bp.response(401, ErrorResponseSchema)
@protected_bp.response(403, ErrorResponseSchema)
@jwt_required(roles=['admin'])
def admin_endpoint():
    """Admin-only endpoint - requires admin role"""
    user_claims = request.user_claims
    
    return jsonify({
        'message': 'This is an admin-only endpoint',
        'admin_user': user_claims['username'],
        'admin_actions': ['view_all_users', 'manage_roles', 'system_config']
    }), 200

@protected_bp.route('/user-data', methods=['GET'])
@protected_bp.doc(security=[{"bearerAuth": []}])
@protected_bp.response(200, UserDataResponseSchema)
@protected_bp.response(401, ErrorResponseSchema)
@protected_bp.response(403, ErrorResponseSchema)
@jwt_required(roles=['user', 'admin'])
def user_data_endpoint():
    """User data endpoint - requires user or admin role"""
    user_claims = request.user_claims
    
    return jsonify({
        'message': 'User data endpoint',
        'user': {
            'id': user_claims['user_id'],
            'username': user_claims['username'],
            'email': user_claims['email'],
            'roles': user_claims['roles']
        }
    }), 200