# cmbs_reminder_system/main.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
import uvicorn
import datetime
import time
import threading
import requests
from dotenv import load_dotenv
from models import Task, ReminderRequest, ReminderResponse
from agents.task_manager import TaskManagerAgent
from agents.contextualizer import ContextualizerAgent
from agents.prompt_generator import GenAIPromptGeneratorAgent
from agents.notification import NotificationAgent
from agents.orchestrator import OrchestratorAgent
from agents.base import r # Import Redis client to clear keys
# Load environment variables from .env file at the very beginning
load_dotenv() # <--- Call load_dotenv() here
app = FastAPI(title="CMBS Automated Reminder Service", version="1.0.0")

task_manager_agent = TaskManagerAgent()
contextualizer_agent = ContextualizerAgent()
genai_prompt_generator_agent = GenAIPromptGeneratorAgent()
notification_agent = NotificationAgent()
orchestrator_agent = OrchestratorAgent(
    task_manager=task_manager_agent,
    contextualizer=contextualizer_agent,
    prompt_generator=genai_prompt_generator_agent,
    notifier=notification_agent
)

def populate_initial_tasks():
    print("\n--- Populating initial tasks ---")
    for key in r.keys("task:*"): r.delete(key)
    r.set("next_task_id", 1)

    task_manager_agent.add_task({
        "description": "Collect Q1 2025 Financial Statements",
        "due_date": datetime.date(2025, 7, 15),
        "assigned_to": "alice.smith@cmbs.com",
        "priority": "Critical",
        "task_type": "Financial Statement Collection",
        "property_id": "PROP-GRND",
        "loan_id": "LOAN-GWR-001",
        "last_update_date": datetime.date(2025, 7, 10),
        "last_update_notes": "Reached out to property manager for update. No response yet.",
        "dependencies": ["TASK-0001", "TASK-0002"]
    })
    # Dummy dependencies for the overdue task
    task_manager_agent.add_task({"task_id": "TASK-0001", "description": "Verify Contact", "due_date": datetime.date(2025, 7, 1), "assigned_to": "system@cmbs.com", "status": "Completed"})
    task_manager_agent.add_task({"task_id": "TASK-0002", "description": "Previous Financials Uploaded", "due_date": datetime.date(2025, 7, 5), "assigned_to": "system@cmbs.com", "status": "Completed"})
    
    task_manager_agent.add_task({
        "description": "Q2 2025 Covenant Compliance Review",
        "due_date": datetime.date(2025, 7, 25),
        "assigned_to": "bob.jones@cmbs.com",
        "priority": "High",
        "task_type": "Covenant Review",
        "property_id": "PROP-RETAIL",
        "loan_id": "LOAN-RT-002",
        "last_update_date": datetime.date(2025, 7, 18),
        "last_update_notes": "Started data aggregation for review."
    })
    print("--- Initial tasks populated ---")


@app.on_event("startup")
async def startup_event():
    print("FastAPI application starting up...")
    populate_initial_tasks()
    scheduler_thread = threading.Thread(target=run_scheduler_periodically, daemon=True)
    scheduler_thread.start()
    print("Scheduler thread started.")

@app.post("/check_reminders", response_model=List[ReminderResponse])
async def check_reminders_endpoint(current_date: datetime.date = datetime.date.today()):
    return orchestrator_agent.process_reminder_request(ReminderRequest(current_date=current_date))

def run_scheduler_periodically():
    while True:
        print("\n--- Background Scheduler: Triggering reminder check ---")
        try:
            requests.post(f"http://127.0.0.1:8000/check_reminders", json={"current_date": datetime.date.today().isoformat()})
            print("Background Scheduler: Reminder check initiated.")
        except Exception as e:
            print(f"Background Scheduler: Error triggering reminders: {e}")
        time.sleep(60)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)