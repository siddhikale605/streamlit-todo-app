import streamlit as st
from datetime import datetime, timedelta
import json
import pandas as pd
import random
import os

# --- App config ---
st.set_page_config(page_title="📱 To-Do App", layout="centered", initial_sidebar_state="collapsed")

# --- Custom CSS to make it app-like ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 20px;
        font-size: 16px;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .stTextInput > div > input,
    .stDateInput > div,
    .stSelectbox > div {
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ccc;
    }

    .stProgress > div > div {
        background-color: #1f77b4;
        height: 20px;
        border-radius: 10px;
    }

    .main {
        max-width: 480px;
        margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- Init ---
TASK_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks():
    with open(TASK_FILE, "w") as f:
        json.dump(st.session_state.todos, f, indent=4)

if "todos" not in st.session_state:
    st.session_state.todos = load_tasks()

# --- Title & Header ---
st.title("📱 To-Do App")
st.markdown("### ✅ Your Personal Task Manager\nWelcome back! Ready to crush your goals today?")

# --- Add Task Form ---
with st.form("add_task"):
    task = st.text_input("📝 Task")
    due_date = st.date_input("📅 Due Date")
    priority = st.selectbox("🔥 Priority", ["Low", "Medium", "High"])
    submitted = st.form_submit_button("➕ Add Task")
    if submitted:
        if task:
            st.session_state.todos.append({
                "task": task,
                "due_date": str(due_date),
                "priority": priority,
                "done": False
            })
            save_tasks()
            st.success("Task added!")
        else:
            st.warning("Task cannot be empty.")

# --- Search ---
search_query = st.text_input("🔍 Search Tasks")

# --- Task List ---
st.subheader("📋 Your Tasks")

if not st.session_state.todos:
    st.info("No tasks yet. Add one above.")
else:
    for i, todo in enumerate(st.session_state.todos):
        if search_query.lower() not in todo["task"].lower():
            continue

        col1, col2, col3, col4 = st.columns([0.05, 0.5, 0.2, 0.25])
        done = col1.checkbox("", value=todo["done"], key=f"done_{i}")
        if done != todo["done"]:
            st.session_state.todos[i]["done"] = done
            save_tasks()

        task_text = f"{'~~' if done else ''}{todo['task']} ({todo['priority']}) - Due: {todo['due_date']}{'~~' if done else ''}"

        if todo["priority"] == "High":
            col2.markdown(f"<span style='color:red'>{task_text}</span>", unsafe_allow_html=True)
        elif todo["priority"] == "Medium":
            col2.markdown(f"<span style='color:orange'>{task_text}</span>", unsafe_allow_html=True)
        else:
            col2.markdown(task_text)

        due = datetime.strptime(todo["due_date"], "%Y-%m-%d").date()
        if not done and due <= datetime.now().date() + timedelta(days=1):
            col4.markdown("🔔 <span style='color:red'>Due Soon!</span>", unsafe_allow_html=True)

# --- Progress Bar ---
total = len(st.session_state.todos)
completed = sum(1 for t in st.session_state.todos if t["done"])
progress = int((completed / total) * 100) if total > 0 else 0
st.progress(progress)
st.caption(f"✅ {completed}/{total} tasks completed")

# --- Charts ---
if st.session_state.todos:
    st.subheader("📊 Task Breakdown")
    df = pd.DataFrame(st.session_state.todos)
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(df['priority'].value_counts())
    with col2:
        status_df = pd.DataFrame({
            "Status": ["Completed", "Pending"],
            "Count": [completed, total - completed]
        })
        st.bar_chart(status_df.set_index("Status"))

# --- Due/Overdue Reminder ---
st.subheader("⏰ Due or Overdue")
today = datetime.now().date()
due_tasks = [t for t in st.session_state.todos if not t["done"] and datetime.strptime(t["due_date"], "%Y-%m-%d").date() <= today]
if due_tasks:
    for t in due_tasks:
        st.error(f"⚠️ {t['task']} (Due: {t['due_date']}) - Priority: {t['priority']}")
else:
    st.success("🎉 No due or overdue tasks!")

# --- Buttons Row ---
colA, colB, colC = st.columns(3)
with colA:
    if st.button("🧹 Clear Completed"):
        st.session_state.todos = [t for t in st.session_state.todos if not t["done"]]
        save_tasks()
        st.success("Cleared completed tasks.")

with colB:
    if st.button("💾 Save to File"):
        save_tasks()
        st.success("Tasks saved!")

with colC:
    if st.button("📂 Load from File"):
        st.session_state.todos = load_tasks()
        st.success("Tasks loaded!")

# --- Daily Motivation ---
st.markdown("---")
st.subheader("💡 Motivation of the Day")
quotes = [
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Don’t stop when you’re tired. Stop when you’re done.",
    "The secret of getting ahead is getting started.",
]
st.info(random.choice(quotes))

# --- Random Task Picker ---
if st.button("🎲 Suggest a Random Task"):
    pending = [t["task"] for t in st.session_state.todos if not t["done"]]
    if pending:
        st.warning(f"Try working on: **{random.choice(pending)}**")
    else:
        st.success("All tasks done! 🎉")
