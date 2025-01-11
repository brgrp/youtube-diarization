import streamlit as st
import requests
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
