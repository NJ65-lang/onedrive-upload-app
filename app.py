import streamlit as st
import traceback

st.title("🔧 Debug Mode - Check Secrets & Imports")

# Step A – Test secret retrieval
st.write("CLIENT_ID:", st.secrets.get("CLIENT_ID"))
st.write("TENANT_ID:", st.secrets.get("TENANT_ID"))
st.write("CLIENT_SECRET:", st.secrets.get("CLIENT_SECRET")[:3] + "…")

# Step B – Test import and availability of msal
try:
    import msal
    st.success("msal imported successfully!")
except Exception as e:
    st.error("Failed to import msal")
    st.text(traceback.format_exc())
    st.stop()

# Step C – Test token fetch
try:
    app = msal.ConfidentialClientApplication(
        st.secrets["CLIENT_ID"],
        authority=f"https://login.microsoftonline.com/{st.secrets['TENANT_ID']}",
        client_credential=st.secrets["CLIENT_SECRET"]
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    st.write("Token result keys:", list(result.keys()))
    if "access_token" in result:
        st.success("🎉 Access token success")
    else:
        st.error("Token fetch failed")
        st.text(str(result))
except Exception as e:
    st.error("Exception during token fetch")
    st.text(traceback.format_exc())
