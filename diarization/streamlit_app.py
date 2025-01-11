import streamlit as st
import requests
import json
import os
from celery_task import download_diarize_transcribe


# Function to start a new task
def start_task(url, output_folder):
    task = download_diarize_transcribe.delay(url, output_folder)
    return task.id

# Function to check the status of a task using Flower API
def check_task_status(task_id):
    flower_url = f"http://localhost:5555/api/task/info/{task_id}"
    response = requests.get(flower_url)
    if response.status_code == 200:
        task_info = response.json()
        return task_info.get("state"), task_info.get("result")
    else:
        return "UNKNOWN", None

# Function to load previous task results
def load_previous_tasks():
    # This function should load the previous task results from a persistent storage
    # For demonstration purposes, we will use a static list
    previous_tasks = [
        {'status': 'success', 'protocol_file': 'test1/20250111_How_To_Build_The_Future__Parker_Conrad/protocol.json'},
        # Add more task results here
    ]
    return previous_tasks

# Streamlit UI
st.title("YouTube Video Diarization")

url = st.text_input("YouTube URL")
output_folder = st.text_input("Output Folder")

if st.button("Start Task"):
    if url and output_folder:
        task_id = start_task(url, output_folder)
        st.write(f"Task started with ID: {task_id}")
    else:
        st.error("Please provide both YouTube URL and Output Folder.")

task_id = st.text_input("Task ID to check status")
if st.button("Check Status"):
    if task_id:
        status, result = check_task_status(task_id)
        st.write(f"Task Status: {status}")
        if status == 'SUCCESS':
            st.write("Diarization and transcription completed.")
            st.write(result)
        elif status == 'FAILURE':
            st.write("Task failed.")
            st.write(result)
        elif status == 'PENDING':
            st.write("Task is pending.")
        elif status == 'STARTED':
            st.write("Task has started.")
        elif status == 'RETRY':
            st.write("Task is being retried.")
        else:
            st.write("Task status is unknown.")
    else:
        st.error("Please provide a task ID.")

# Load previous task results
previous_tasks = load_previous_tasks()
task_options = [f"{task['protocol_file']} ({task['status']})" for task in previous_tasks]

selected_task = st.selectbox("Select a previous task to view the protocol", task_options)

if selected_task:
    selected_protocol_file = "diarization/"+next(task['protocol_file'] for task in previous_tasks if f"{task['protocol_file']} ({task['status']})" == selected_task)
    st.write(f"Displaying protocol: {selected_protocol_file}")
    if os.path.exists(selected_protocol_file):
        with open(selected_protocol_file, 'r') as file:
            protocol_content = json.load(file)
            st.json(protocol_content)
    else:
        st.error(f"Protocol file not found: {selected_protocol_file}")
