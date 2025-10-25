import streamlit as st
import time
from datetime import datetime
import asyncio
from src.discord_notify import send_discord_alert
from src.twilio_caller import call_all_emergency_contacts, make_voice_call_to_police, get_twilio_status

def render_panic_button(last_emergency_data):
    """
    Renders the panic button and its logic, now as a simple button.
    """
    st.markdown("---")
    st.markdown("### Advanced Alert")
    st.caption("This will initiate automated calls to police and SMS to emergency contacts.")

    if not st.session_state.call_in_progress and not st.session_state.call_completed:
        if st.button("🚨 Initiate Emergency Call Sequence", key="panic_btn"):
            st.session_state.call_in_progress = True
            st.rerun()

    if st.session_state.call_in_progress and not st.session_state.call_completed:
        st.info("📞 Connecting to Emergency Services...")
        
        progress_bar = st.progress(0, text="Initiating sequence...")
        emergency_type = last_emergency_data.get("emergency_type", "emergency")
        location = "Bengaluru, Karnataka" # You can make this dynamic later
        user_message = last_emergency_data.get("user", "Emergency reported")

        # Step 1: Call police
        progress_bar.progress(10, text="Calling police...")
        police_result = make_voice_call_to_police(emergency_type, location)
        time.sleep(1)

        # Step 2: Notify emergency contacts
        progress_bar.progress(50, text="Notifying emergency contacts via SMS...")
        contact_results = call_all_emergency_contacts(emergency_type, location, last_emergency_data)
        time.sleep(2)
        
        # Step 3: Send a detailed log to Discord
        progress_bar.progress(80, text="Logging event to Discord...")
        call_log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": location,
            "emergency_type": emergency_type,
            "user_message": user_message
        }
        discord_message = f"""**Advanced Alert Log**
        > **Time:** {call_log['timestamp']}
        > **Location:** {call_log['location']}
        > **Emergency:** {call_log['emergency_type'].title()}
        > **Reported:** "{call_log['user_message']}"
        > **Police Status:** `{'Success/Simulated' if police_result.get('status') != 'failed' else 'Failed'}`
        > **Contacts Status:** `Notified/Simulated`"""
        try:
            asyncio.run(send_discord_alert(discord_message))
        except Exception as e:
            st.error(f"Discord log failed: {e}")
        
        progress_bar.progress(100, text="Sequence complete.")
        time.sleep(1)

        st.session_state.police_call = police_result
        st.session_state.contact_calls = contact_results
        st.session_state.call_completed = True
        st.session_state.call_in_progress = False
        st.rerun()

    if st.session_state.call_completed:
        st.success("Advanced Alert Sequence Completed")

        # Display Police Call Results
        if hasattr(st.session_state, 'police_call') and st.session_state.police_call:
            st.subheader("Police Call")
            pc = st.session_state.police_call
            status = pc.get('status', 'N/A')
            if status in ['calling', 'queued', 'ringing', 'in-progress', 'completed']: st.success(f"✓ Call Status: {status.capitalize()}")
            elif status == 'simulated': st.info(f"**Simulated Call** (Twilio not configured)")
            elif status == 'not_configured': st.warning("Police number not configured in .env")
            else: st.error(f"Call failed: {pc.get('error', status)}")

        # Display Emergency Contacts Results
        if hasattr(st.session_state, 'contact_calls') and st.session_state.contact_calls:
            st.subheader("Emergency Contacts SMS")
            for name, result in st.session_state.contact_calls.items():
                if name == 'police': continue # Don't show police in this list
                if result['status'] == 'sent': st.success(f"✓ {name}: SMS sent")
                elif result['status'] == 'simulated': st.info(f"○ {name}: Simulated SMS")
                elif result['status'] == 'not_configured': st.warning(f"⚠ {name}: Not configured")
                else: st.error(f"✗ {name}: Failed")
        
        if st.button("Reset Sequence", key="reset_btn"):
            keys_to_clear = ['call_completed', 'call_in_progress', 'police_call', 'contact_calls']
            for key in keys_to_clear:
                if hasattr(st.session_state, key): delattr(st.session_state, key)
            st.rerun()