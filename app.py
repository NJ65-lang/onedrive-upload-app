import streamlit as st
from msal import ConfidentialClientApplication
import requests
import os

# Azure AD app credentials
CLIENT_ID = "60caa29e-c194-4d2b-bb3f-de9772859d24"
TENANT_ID = "2ab5ad56-39a5-4e36-b54e-d58d6ef2353d"
CLIENT_SECRET = "36c69991-1504-4d7e-bf1d-6fd37ae80ca6"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

# Folder mapping: Display name -> OneDrive folder name
FOLDER_OPTIONS = {
    "MASTER COURSE OUTLINE DATABASE": "MASTER COURSE OUTLINE DATABASE",
    "TRAINER PROFILE DATABASE": "TRAINER PROFILE DATABASE",
    "LAB SETUP DATABASE": "LAB SETUP DATABASE"
}

def get_access_token():
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" in result:
        return result["access_token"]
    else:
        st.error("Error obtaining access token: " + str(result.get("error_description")))
        return None

def upload_file_to_onedrive(access_token, folder_name, file):
    # Microsoft Graph API endpoint for OneDrive root children
    # We'll upload files inside the folder by path:
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_name}/{file.name}:/content"
    
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": file.type
    }
    response = requests.put(upload_url, headers=headers, data=file.getvalue())
    if response.status_code == 201 or response.status_code == 200:
        return True, response.json().get("webUrl", "")
    else:
        return False, response.text

def main():
    st.title("📁 Real OneDrive Upload & RAG App")

    selected_folder = st.selectbox("Choose OneDrive Folder to Upload Into", list(FOLDER_OPTIONS.keys()))
    uploaded_file = st.file_uploader("Upload your file here")

    if uploaded_file is not None:
        token = get_access_token()
        if token:
            with st.spinner("Uploading file to OneDrive..."):
                success, info = upload_file_to_onedrive(token, FOLDER_OPTIONS[selected_folder], uploaded_file)
            if success:
                st.success(f"File uploaded successfully! [Open File]({info})")
            else:
                st.error(f"Upload failed: {info}")

    st.divider()
    query = st.text_input("🔍 Ask a question about your files (Coming Soon)")
    if query:
        st.info(f"Search results for: '{query}' (Functionality coming soon)")

if __name__ == "__main__":
    main()
