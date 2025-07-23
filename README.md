# Fin-GenAI-Reminder-Engine
Multi-agent system for generating highly contextual and actionable follow-up reminders in an asset management context. 
CMBS-GenAI-Reminder-Engine
# 🚀 Project Overview
This project demonstrates a modular, multi-agent system for generating highly contextual and actionable follow-up reminders in a CMBS (Commercial Mortgage-Backed Securities) asset management context. Moving beyond simple calendar alerts, this system uses Generative AI to synthesize data from various sources and create personalized, insightful messages for asset managers.

# The core technology stack includes:

* Python 3.11+

* FastAPI: To provide a robust and scalable API interface.

* Multi-Agent Communication Protocol (MCP): A design pattern that breaks down complex workflows into specialized, communicating agents.

* Redis: A high-speed, in-memory data store used for persistent agent memory and contextual data caching during the reminder process.

* Google Gemini LLM: Integrated for intelligently crafting detailed, context-aware reminder messages.

# 💡 Why Generative AI?
The key value of this system lies in its ability to generate reminders that are more than just notifications. While a traditional system can easily query a database for an overdue task, it struggles to:

Provide Actionable Insights: Instead of saying "Task is overdue," it can suggest specific next steps based on the last update and known dependencies.

Communicate Urgency and Impact: It can explain why a task is critical by referencing loan covenants, market conditions, or its role in a broader workflow.

Adapt to Context: It dynamically changes its tone and content based on a multitude of factors (task type, priority, time overdue, etc.) without requiring a massive library of rigid if/else templates.

Generative AI transforms a system-generated alert into a professional, coaching-style message that drives better and more timely outcomes.

# 🏗️ System Architecture (MCP Design)
The system is built on a Multi-Agent Communication Protocol (MCP) design, where each agent is a specialized, autonomous component with a clear role.

Orchestrator Agent: The central coordinator. It receives a request to check for reminders and delegates the workflow to the other agents in the correct sequence.

Task Manager Agent: Manages all task data. It stores task information persistently in Redis, handles task creation and status updates, and is responsible for identifying which tasks require a reminder based on due dates and last reminder timestamps.

Contextualizer Agent: Gathers and synthesizes all relevant contextual data for a given task. This includes details about the associated property and loan, as well as external insights like market news (mocked in this example). This data is also stored/retrieved from Redis for efficiency.

GenAI Prompt Generation Agent: The core of the intelligence. It receives the rich context from the Contextualizer and constructs a detailed prompt for the Google Gemini LLM. It then receives the LLM's output and formats it for notification.

Notification Agent: The final-mile agent. It takes the professionally crafted message and sends it to the assigned user via a communication channel (e.g., email, Slack).

# 💾 Role of Redis
In this architecture, Redis is used as a fast, in-memory data store that acts as a shared, temporary memory for the agents. It is not the primary database of record for all CMBS data. Its role is to:

Persistent Agent Memory: Store task objects and their state (status, last_reminder_sent) so agents can maintain state across invocations.

Context Caching: Cache frequently accessed contextual data (e.g., property details, loan covenants) to avoid slow queries to a primary SQL database during the time-sensitive reminder generation process.

Inter-Agent Data Sharing: Provide a central place for agents to store and retrieve data relevant to the current process flow.


### 🚀 Getting Started
#### Prerequisites
* Python 3.11+

* Docker: Recommended for running Redis locally.

* Google Gemini API Key: Obtain one from Google AI Studio.


## 1. Installation
Start Redis: The easiest way is with Docker:

```Bash

docker run -p 6379:6379 --name my-redis -d redis/redis-stack-server:latest
Create and activate a virtual environment:
```
```Bash

python3.11 -m venv venv # Use python3.11 explicitly
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
### Install dependencies:
Save the following to requirements.txt:

fastapi
uvicorn
pydantic
redis
requests
google-generativeai # New dependency for Gemini
Then run:

```Bash

pip install -r requirements.txt
```
## 2. Setting Up Your Gemini API Key
You must set your Gemini API key as an environment variable before running the application. Replace 'YOUR_GEMINI_API_KEY_HERE' with your actual key.

On Linux/macOS (for current session):

```Bash

export GOOGLE_API_KEY='YOUR_GEMINI_API_KEY_HERE'
On Windows (Command Prompt, for current session):
```
```DOS

set GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE
On Windows (PowerShell, for current session):
```
```PowerShell

$env:GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```
For permanent setup, refer to your operating system's documentation for adding environment variables.

## 3. Running the Application
Navigate into the CMBS-GenAI-Reminder-Engine directory in your terminal.

### Run the FastAPI app:

```Bash

uvicorn main:app --reload --port 8000
```
This will start the API server and the background scheduler. The console output will show agents initializing, dummy data being populated into Redis, and the scheduler triggering a reminder check periodically. When a reminder is due, you'll see the GenAIPromptGeneratorAgent making a call to Gemini and the NotificationAgent printing the generated email.

### Access the API:

Open your browser to http://127.0.0.1:8000/docs to see the interactive API documentation.

You can manually trigger a reminder check or retrieve task details from here.

