from keycloak import KeycloakOpenID, exceptions

# Configure client
keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8080",
    client_id="streamlit-app",
    realm_name="TKSSO",
    # client_secret_key="your-client-secret"
)

def check_user(current_user_id, password):
    try:
        token = keycloak_openid.token(
            username=current_user_id,
            password=password)
        
        return token
    except exceptions.KeycloakAuthenticationError:
        return False

# Use token for requests
#access_token = token['access_token']
#refresh_token = token['refresh_token']

# Get user info
#userinfo = keycloak_openid.userinfo(access_token)
#print(userinfo)

if __name__ == '__main__':
    res = check_user('dima', 'dima')    
    print(res)