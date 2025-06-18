import streamlit as st
from msal import ConfidentialClientApplication
import requests

# Azure AD app credentials from Streamlit secrets
CLIENT_ID = st.secrets["CLIENT_ID"]
TENANT_ID = st.secrets["TENANT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

# Folder mapping: Display name -> OneDrive folder name
FOLDER_OPTIONS = {
    "MASTER COURSE OUTLINE DATABASE": "MASTER COURSE OUTLINE DATABASE",
    "TRAINER PROFILE DATABASE": "TRAINER PROFILE DATABASE",
    "LAB SETUP DATABASE": "LAB SETUP DATABASE"
}

def get_access_token():
    try:
        app = ConfidentialClientApplication(
            st.secrets["CLIENT_ID"],
            authority=f"https://login.microsoftonline.com/{st.secrets['TENANT_ID']}",
            client_credential=st.secrets["CLIENT_SECRET"]
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        
        if "access_token" in result:
            st.success("✅ Access token acquired successfully.")
            return result["access_token"]
        else:
            st.error("❌ Failed to get token.")
            st.json(result)  # Print the full error
            return None
    except Exception as e:
        st.error(f"💥 Exception while getting token: {e}")
        return None

def upload_file_to_onedrive(access_token, folder_name, file):
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_name}/{file.name}:/content"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": file.type
    }
    response = requests.put(upload_url, headers=headers, data=file.getvalue())

    if response.status_code in [200, 201]:
        return True, response.json().get("webUrl", "")
    else:
        return False, response.text

def main():
    st.title("📁 Real OneDrive Upload & RAG App")

    try:
        selected_folder = st.selectbox("Choose OneDrive Folder to Upload Into", list(FOLDER_OPTIONS.keys()))
        uploaded_file = st.file_uploader("Upload your file here")

        if uploaded_file is not None:
            token = get_access_token()
            if token:
                with st.spinner("Uploading file to OneDrive..."):
                    success, info = upload_file_to_onedrive(token, FOLDER_OPTIONS[selected_folder], uploaded_file)
                if success:
                    st.success(f"✅ File uploaded successfully! [Open File]({info})")
                else:
                    st.error("❌ Upload failed")
                    st.text(info)
            else:
                st.error("⚠️ Could not get access token.")
    except Exception as e:
        st.error("💥 App crashed with exception:")
        st.exception(e)

    st.divider()
    st.text("🔍 Search functionality coming soon...")
    st.stop()  # Stops execution to avoid blinking
