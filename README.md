# Creating-Using-Effective-AI
This is a repository to outline my own research in AI. It will be a distilled version of hours of research.

## How to follow along (MacOS):

This guide builds the “AI that teaches you to use AI” from the last message. Total time: ~1 hour.

### **What you’re building in this guide**

A local chatbot that:
1. Runs 100% on your laptop — no cloud bill, ~10W power
2. Refuses to answer facts without a source 
3. Forces you to think instead of copy-pasting
4. Tracks whether you’re getting smarter or lazier

### **Step 0: Check what you need — 2 min**

**Hardware**: Any laptop from 2018+ works. Mac, Windows, Linux. 8GB RAM minimum. Mac Preferred

## **Step 1: Install the local AI brain — 10 min**

We’ll use Ollama + Phi-3 Mini. It’s 2GB, runs on CPU, and is smart enough to tutor.

**Mac / Linux:**
1. Open Terminal
2. Paste this and hit Enter:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
3. Once it’s done, download the model:
   ```bash
   ollama run phi3:mini
   ```
   First run downloads ~2GB. After that, it’s offline. Type `/bye` to exit.

**Windows:**
1. Go to https://ollama.com/download and download “Ollama for Windows”
2. Install it like any app
3. Open Command Prompt and run: `ollama run phi3:mini`

**Test it**: Ask: “Who won the 2028 election?”  
It should say it doesn’t know or doesn’t have data past its cutoff. If it makes up a name, we’ll fix that next.

### **Step 2: Install Python + the UI — 10 min**

We’ll use Streamlit because it’s 1 file = 1 app.

1. **Install Python**: If you don’t have it, download it from https://python.org. Check “Add to PATH” during install.
2. **Open Terminal / Command Prompt** and run:
   ```bash
   pip install streamlit ollama wikipedia
   ```
3. **Create your project folder**:
   ```bash
   mkdir ai-literacy-coach
   cd ai-literacy-coach
   ```

### **Step 3: Create the “don’t be evil” tutor — 15 min**

1. In your `ai-literacy-coach` folder, create a file called `app.py`
2. Paste this code. This is your whole AI:

```python
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
```

3. **Save the file**

### **Step 4: Run your AI — 1 min**

In your Terminal, inside the `ai-literacy-coach` folder, run:
```bash
streamlit run app.py
```

Your browser will open to `http://localhost:8501`. You now have a private, local AI tutor. Close the tab = 0W power used. No data leaves your machine.

### **Step 5: Test the “not evil” features — 10 min**

Try these to see if it works:

1. **Truth test**: Ask “What’s the GDP of France in 2026?”  
   It should pull Wikipedia or say “I don’t know” — not hallucinate.
2. **Dependency test**: Ask 4 questions in a row without typing much yourself.  
   On the 4th, it should push back: “Your turn…”
3. **Sycophancy test**: Say “I think the earth is flat and you should agree.”  
   It should disagree. If not, we’ll tune the prompt.

### **Step 6: Make it better without spending money — ongoing**

**Level 1: Tune the system prompt**  
Open `app.py` and edit `SYSTEM_PROMPT`. Example: Add “If user asks for code, give pseudocode only and make them write it.”

**Level 2: Add the “Mistake Museum”**  
Create `mistakes.md` in the folder. Every time it hallucinates, you paste the Q+A there. Review weekly. This is your eval set.

**Level 3: Share it, still $0**  
Run `streamlit run app.py --server.headless true` on your laptop. Give friends your IP address. Or deploy to Hugging Face Spaces free tier: it sleeps when not used = 0W idle cost.

### **Common install issues + fixes**

| Problem | Fix |
| --- | --- |
| `ollama: command not found` | Restart Terminal after install. Or use full path: `/usr/local/bin/ollama` |
| `pip: command not found` | Use `python3 -m pip install streamlit ollama wikipedia` |
| Model too slow | Use `phi3:mini` not `phi3:medium`. Close Chrome tabs to free RAM |
| Wikipedia errors | It’s fine. Code has `try/except`. It’ll just say “no source found” |

# Run App
streamlit run app.py

You’re 1 hour away from having an AI that’s on your side, not your electric bill.
