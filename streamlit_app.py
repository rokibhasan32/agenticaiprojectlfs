import streamlit as st
import requests

st.title("DIU Library AI Agent 📚")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask the library assistant..."):
    try:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response with error handling
        response = requests.post(
            "http://localhost:8000/query/",  # Corrected endpoint
            json={"user_input": prompt},  # Matches FastAPI request format
            timeout=10  # Add timeout
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse JSON response
        response_data = response.json()
        
        # Get response text with fallback
        ai_response = response_data.get("response", "Sorry, I couldn't process that request.")

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        
        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        with st.chat_message("assistant"):
            st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        with st.chat_message("assistant"):
            st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})