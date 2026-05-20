import streamlit as st
import ollama
import wikipedia
import sqlite3
from datetime import datetime

# Step 1: Setup local database to track dependency
conn = sqlite3.connect('progress.db')
conn.execute('''CREATE TABLE IF NOT EXISTS logs
             (timestamp TEXT, human_words INT, ai_words INT)''')

st.title("AI Literacy Coach")
st.caption("Goal: Make you better at using AI, not dependent on it")

# Step 2: The "don't be evil" system prompt
SYSTEM_PROMPT = """
You are an AI Literacy Coach. Your job is to make the human smarter, not dependent.

Rules:
1. If the question is factual, search Wikipedia first. Cite the article title. If not found, say "I don't know. Here's how to research it:" and teach them.
2. Never give direct answers to homework/creative work. Instead, ask Socratic questions.
3. Every 3rd response, you must ask the human a question instead of answering.
4. If the human hasn't typed >20 words in their last 2 messages, say: "Your turn. Summarize what you know so far."
5. Be truth-seeking, not agreeable. Disagree with the user if they're wrong.
"""

# Step 3: Helper to get Wikipedia summary = low-power "search"
def get_wiki(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except:
        return None

# Step 4: Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me, but be ready to think"):
    # Log human words for dependency score
    human_words = len(prompt.split())
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Try to ground in Wikipedia first = truth + low power
        wiki_context = get_wiki(prompt)
        full_prompt = f"Wikipedia context: {wiki_context}\n\nUser question: {prompt}"
        
        response = ollama.chat(model='phi3:mini', messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_prompt}
        ])
        
        ai_reply = response['message']['content']
        ai_words = len(ai_reply.split())
        
        # Save dependency score
        conn.execute("INSERT INTO logs VALUES (?, ?, ?)", 
                    (datetime.now(), human_words, ai_words))
        conn.commit()
        
        st.markdown(ai_reply)
        
        # Show dependency meter
        ratio = ai_words / max(human_words, 1)
        if ratio > 5:
            st.warning("Dependency alert: You're letting me talk 5x more than you. Try answering first next time.")
        
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
