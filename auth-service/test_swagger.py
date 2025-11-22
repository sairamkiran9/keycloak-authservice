#!/usr/bin/env python3
"""
Quick test script to verify Swagger/OpenAPI documentation is working
"""

import requests
import sys

def test_swagger_endpoints():
    """Test that Swagger UI and API documentation endpoints are accessible"""
    base_url = "http://localhost:5000"
    
    endpoints_to_test = [
        ("/health", "Health check"),
        ("/swagger-ui", "Swagger UI"),
        ("/openapi.json", "OpenAPI spec"),
        ("/redoc", "ReDoc documentation")
    ]
    
    print("Testing Swagger/OpenAPI endpoints...")
    print("=" * 50)
    
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✓ PASS" if response.status_code == 200 else f"✗ FAIL ({response.status_code})"
            print(f"{status} - {description}: {endpoint}")
        except requests.exceptions.RequestException as e:
            print(f"✗ ERROR - {description}: {endpoint} - {str(e)}")
    
    print("\n" + "=" * 50)
    print("Swagger UI: http://localhost:5000/swagger-ui")
    print("ReDoc: http://localhost:5000/redoc")
    print("OpenAPI Spec: http://localhost:5000/openapi.json")

if __name__ == "__main__":
    test_swagger_endpoints()