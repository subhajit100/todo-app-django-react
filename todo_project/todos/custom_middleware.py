# myapp/token_refresh_middleware.py
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from django.http import JsonResponse
from todos.helper import cookie_options

class TokenRefreshMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Define the routes to exclude from middleware
        excluded_routes = ["/api/login", "/api/register", "/api/check-auth"]

        if request.path.startswith("/api"):
            # Skip middleware logic for excluded routes
            if any(route in request.path for route in excluded_routes):
                return
                
            
            # auth_header = request.META.get('HTTP_AUTHORIZATION', None)
            access_token = request.COOKIES.get('access_token', None)

            # # if access_token and access_token.startswith('Bearer '):
            # if not access_token:
            #     # access_token = access_token.split(' ')[1]
            #     try:
            #         # Validate the access token
            #         AccessToken(access_token)
            #     except TokenError as e:
                    # # If the access token has expired
                    # print('inside token error with e: ', e)
                    # if 'Token is invalid or expired' in str(e):
            if not access_token:        
                refresh_token = request.COOKIES.get('refresh_token')
                if refresh_token:
                    try:
                        # Refresh the access token
                        new_access_token = str(RefreshToken(refresh_token).access_token)
                        # Add the new access token to the request
                        # request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'
                        request.COOKIES['access_token'] = new_access_token
                        # Optionally, add the new token to the response headers
                        request.new_access_token = new_access_token
                    except TokenError:
                        return JsonResponse(
                            {'error': 'Invalid or expired refresh token'},
                            status=status.HTTP_401_UNAUTHORIZED
                        )
                else:
                    return JsonResponse(
                        {'error': 'No refresh token provided'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
        return None

    def process_response(self, request, response):
        # If a new access token was generated, include it in the response cookies
        if hasattr(request, 'new_access_token'):
            
            response.set_cookie(
                key='access_token',  # Name of the cookie
                value=request.new_access_token,  # New access token value
                httponly=True,  # Prevent JavaScript from accessing the cookie
                # secure=cookie_options.get('secure', False),  # Send the cookie over HTTPS only (adjust for development)
                # samesite=cookie_options.get('samesite', 'None'),  # Control cross-site cookie behavior
                max_age=cookie_options.get('access_token_expiry_in_minutes', 30) * 60  # Cookie expiration time in seconds (match access token expiry)
            )
        return response
