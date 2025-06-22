import streamlit as st
from keycloak import KeycloakOpenID
import jwt
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
from ui import ui

# Keycloak configuration
KEYCLOAK_URL = "http://localhost:8080"
REALM_NAME = "TKSSO"
CLIENT_ID = "streamlit-app"
#CLIENT_SECRET = "your-client-secret"
REDIRECT_URI = "http://localhost:8501"  # Update for production

# Initialize Keycloak client
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=CLIENT_ID,
    realm_name=REALM_NAME,
)

def decode_token(token):
    """Decode and validate JWT token"""
    try:
        return jwt.decode(
            token,
            key=keycloak_openid.public_key(),
            options={"verify_signature": True, "verify_aud": False},
            algorithms=["RS256"]
        )
    except Exception as e:
        st.error(f"Token validation failed: {e}")
        return None

def login():
    """Show login button and handle authentication"""
    auth_url = keycloak_openid.auth_url(
        redirect_uri=REDIRECT_URI,
        scope="openid email profile",
        state=st.session_state.get('state')
    )
    with st.sidebar:
        st.markdown(f'<a href="{auth_url}" target="_self">Login with Keycloak</a>', unsafe_allow_html=True)
        
    st.session_state.auth_url = auth_url

def logout():
    """Clear session and logout"""
    keycloak_openid.logout(st.session_state["refresh_token"])
    st.session_state.clear()
    streamlit_js_eval(js_expressions="parent.window.location.reload()")

def main():
    st.title("Оперативная аналитика и атоматизация")

    # Check for authentication code in URL
    query_params = st.query_params
    if 'code' in query_params and 'access_token' not in st.session_state:
        try:
            # Exchange code for token
            token = keycloak_openid.token(
                grant_type="authorization_code",
                code=query_params['code'],
                redirect_uri=REDIRECT_URI
            )
            print(2)
            st.session_state.access_token = token['access_token']
            st.session_state.refresh_token = token['refresh_token']
            print(22)
            #st.experimental_set_query_params()
            #print(222)
            
        except Exception as e:
            pass
            #with st.sidebar:
            #    st.write("Залогиньтесь, пожалуйста!")
            #    # st.error(f"Authentication failed: {e}")

    # Show appropriate UI based on auth state
    if 'access_token' in st.session_state:
        current_user_info = keycloak_openid.userinfo(st.session_state['access_token'])
        current_user_id = current_user_info['preferred_username']
        # token_data = st.session_state.decoded_token
        #st.sidebar.success(f"Logged in as {token_data.get('preferred_username', 'User')}")
        
        # Token information
        #with st.expander("Token Details"):
        #st.json(token_data)

        # Session information
        #st.write(f"Session expires at: {datetime.fromtimestamp(token_data['exp'])}")
        
        # Logout button
        with st.sidebar:
            st.text_input("Текущий пользователь:", current_user_id, disabled=True)
            st.button("Выйти из аккаунта", on_click=logout, use_container_width=True)
        
        # Your protected application content here
        #st.success("You're authenticated! Here's your protected content.")
        ui(current_user_id)
        
    else:
        login()

if __name__ == "__main__":
    main()
