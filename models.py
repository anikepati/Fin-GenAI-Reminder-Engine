# CMBS-GenAI-Reminder-Engine/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import datetime

class Task(BaseModel):
    task_id: str = Field(..., description="Unique identifier for the task.")
    description: str = Field(..., description="A brief description of the task.")
    due_date: datetime.date = Field(..., description="The date the task is due.")
    assigned_to: str = Field(..., description="The user or team assigned to the task (e.g., email address).")
    status: str = Field("Pending", description="Current status of the task (e.g., Pending, In Progress, Completed, Overdue).")
    priority: str = Field("Medium", description="Priority level (e.g., Low, Medium, High, Critical).")
    
    # CMBS Specifics
    property_id: Optional[str] = Field(None, description="Associated property ID.")
    loan_id: Optional[str] = Field(None, description="Associated loan ID.")
    task_type: Optional[str] = Field(None, description="Type of task (e.g., 'Financial Statement Collection', 'Inspection Schedule', 'Covenant Review').")
    
    # Dependencies
    dependencies: List[str] = Field([], description="List of task_ids that this task depends on.")
    dependent_tasks_status: Dict[str, str] = Field({}, description="Current status of dependent tasks (task_id: status).")

    # Historical context for Gen AI
    last_update_date: Optional[datetime.date] = None
    last_update_notes: Optional[str] = None
    
    # For reminder tracking
    last_reminder_sent: Optional[datetime.datetime] = None

class PropertyContext(BaseModel):
    property_id: str
    property_type: str
    occupancy_rate: float
    square_footage: Optional[int] = None
    # Add more relevant property details

class LoanContext(BaseModel):
    loan_id: str
    loan_type: str
    maturity_date: datetime.date
    dscr_covenant: Optional[float] = None
    # Add more relevant loan details

class CombinedContext(BaseModel):
    task_context: Task
    property_context: Optional[PropertyContext] = None
    loan_context: Optional[LoanContext] = None
    market_news_summary: Optional[str] = None # Synthesized by Contextualizer

class ReminderRequest(BaseModel):
    task_id: str = Field("scheduler_trigger", description="Identifier for the request; 'scheduler_trigger' for automated runs.")
    current_date: datetime.date

class ReminderResponse(BaseModel):
    task_id: str
    recipient: str
    subject: str
    message: str
    status: str
    error: Optional[str] = None