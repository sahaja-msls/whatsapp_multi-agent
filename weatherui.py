import streamlit as st
# Import your groq logic here
# from your_agent_file import run_weather_agent 
from weather_agent import weather_agent

# --- 1. UI SETUP ---
st.set_page_config(page_title="AI Weather Agent", page_icon="☁️")
st.title("☁️ Live Weather & Data Agent")
st.markdown("Ask me about the weather anywhere in the world. I will fetch live API data to answer you.")

# --- 2. SESSION STATE (Memory for the UI) ---
# Streamlit refreshes the script on every interaction. 
# We use session_state to remember the chat history.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! What city's weather would you like to check today?"}
    ]

# --- 3. DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. USER INPUT & AGENT EXECUTION ---
# st.chat_input creates a text box at the bottom of the screen
if prompt := st.chat_input("E.g., What is the weather like in London right now?"):
    
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Trigger the Agent
    with st.chat_message("assistant"):
        # We use a spinner to show the user the AI is "Thinking" or "Calling an API"
        with st.spinner("Fetching live satellite data..."):
            
            # ⚠️ REPLACE THIS LINE WITH YOUR ACTUAL AGENT FUNCTION
            # Example: ai_response = run_weather_agent(prompt)
            
            # --- MOCK RESPONSE (For testing the UI) ---
            ai_response = weather_agent(prompt)
            # ------------------------------------------
            
            st.markdown(ai_response)
    
    # Save the AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": ai_response})