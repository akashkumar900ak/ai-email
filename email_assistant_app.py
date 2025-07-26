import streamlit as st
import pandas as pd
from datetime import datetime
from classifier import EmailClassifier
from prioritizer import EmailPrioritizer
from reply_generator import ReplyGenerator
from email_client import EmailClient

# Streamlit config
st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="📧",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'emails' not in st.session_state:
    st.session_state.emails = []
if 'selected_email' not in st.session_state:
    st.session_state.selected_email = None

# Load ML components
@st.cache_resource
def load_components():
    classifier = EmailClassifier()
    prioritizer = EmailPrioritizer()
    reply_gen = ReplyGenerator()
    return classifier, prioritizer, reply_gen

classifier, prioritizer, reply_gen = load_components()

def main():
    st.title("📧 AI Email Assistant")
    st.markdown("Classify, prioritize, and auto-reply to emails using AI.")

    with st.sidebar:
        st.header("⚙️ Settings")

        st.subheader("📥 Email Login")
        email_address = st.text_input("Email Address")
        email_password = st.text_input("App Password", type="password")

        if st.button("🔌 Connect"):
            if email_address and email_password:
                try:
                    email_client = EmailClient(email_address, email_password)
                    st.session_state.email_client = email_client
                    st.session_state.authenticated = True
                    st.success("✅ Email connected successfully!")
                except Exception as e:
                    st.error(f"❌ Connection failed: {e}")
            else:
                st.warning("Please provide both email and password.")

        st.subheader("🧪 Demo Mode")
        if st.button("📂 Load Sample Emails"):
            st.session_state.emails = load_sample_emails()
            st.session_state.authenticated = True
            st.success("✅ Sample data loaded.")

        st.subheader("🧠 Model Training")
        if st.button("⚙️ Train AI Models"):
            with st.spinner("Training classifiers..."):
                classifier.train_model()
                prioritizer.train_model()
            st.success("✅ Models trained.")

    if st.session_state.authenticated:
        tab1, tab2, tab3 = st.tabs(["📨 Inbox", "📊 Analytics", "⚙️ Settings"])

        with tab1:
            display_inbox()
        with tab2:
            display_analytics()
        with tab3:
            display_settings()
    else:
        st.info("👈 Connect your email or load sample data to begin.")

def load_sample_emails():
    return [
        {
            'id': 1,
            'subject': 'Project Deadline Tomorrow',
            'sender': 'boss@company.com',
            'body': 'Please send an update. The final report is due by Friday.',
            'date': datetime.now(),
            'classification': 'work',
            'priority': 'high',
            'is_read': False
        },
        {
            'id': 2,
            'subject': 'Coffee This Weekend?',
            'sender': 'friend@email.com',
            'body': 'Hey! Are you free this Sunday for coffee at our usual spot?',
            'date': datetime.now(),
            'classification': 'personal',
            'priority': 'low',
            'is_read': False
        }
    ]

def display_inbox():
    st.header("📨 Inbox")

    if hasattr(st.session_state, 'email_client'):
        if st.button("🔄 Fetch New Emails"):
            with st.spinner("Loading emails..."):
                try:
                    new_emails = st.session_state.email_client.fetch_emails(limit=10)
                    for email in new_emails:
                        email['classification'] = classifier.classify_email(email['subject'] + ' ' + email['body'])
                        email['priority'] = prioritizer.prioritize_email(email)
                    st.session_state.emails = new_emails
                    st.success(f"✅ {len(new_emails)} emails fetched.")
                except Exception as e:
                    st.error(f"❌ Failed to fetch: {e}")

    if st.session_state.emails:
        for email in st.session_state.emails:
            show_email_card(email)
    else:
        st.info("📭 No emails found. Try loading or fetching.")

def show_email_card(email):
    with st.expander(f"📧 {email['subject']}"):
        st.markdown(f"**From:** {email['sender']}")
        st.markdown(f"**Category:** `{email['classification']}` | **Priority:** `{email['priority']}`")
        st.markdown(f"**Received:** {email['date'].strftime('%Y-%m-%d %H:%M')}")
        st.markdown("**Body:**")
        st.write(email['body'])

        reply_key = f"generated_reply_{email['id']}"

        # Step 1: Generate reply
        if st.button("🪄 Generate Reply", key=f"gen_{email['id']}"):
            with st.spinner("Generating..."):
                reply = reply_gen.generate_reply(email['body'], email['classification'])
                st.session_state[reply_key] = reply

        # Step 2: Show editable area
        if reply_key in st.session_state:
            st.text_area("✍️ Review & Edit Reply:", value=st.session_state[reply_key], height=150, key=f"textarea_{email['id']}")

            # Step 3: Send after review
            if st.button("📤 Send This Reply", key=f"send_{email['id']}"):
                if 'email_client' in st.session_state:
                    try:
                        st.info("Sending reply...")
                        success = st.session_state.email_client.send_reply(
                            original_email=email,
                            reply_body=st.session_state[reply_key]
                        )
                        if success:
                            st.success("✅ Reply sent.")
                        else:
                            st.error("❌ Reply failed.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        st.code(f"Sender: {email['sender']}", language="text")

def display_analytics():
    st.header("📊 Email Analytics")

    if st.session_state.emails:
        df = pd.DataFrame(st.session_state.emails)
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("By Category")
            st.bar_chart(df['classification'].value_counts())

        with col2:
            st.subheader("By Priority")
            st.bar_chart(df['priority'].value_counts())
    else:
        st.info("No email data available.")

def display_settings():
    st.header("⚙️ App Settings")
    st.slider("⚖️ AI Confidence Threshold", 0.0, 1.0, 0.8)
    st.markdown("Additional settings coming soon...")

if __name__ == "__main__":
    main()
