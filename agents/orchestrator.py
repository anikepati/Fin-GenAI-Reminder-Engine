# cmbs_reminder_system/agents/orchestrator.py
from .base import Agent
from .task_manager import TaskManagerAgent
from .contextualizer import ContextualizerAgent
from .prompt_generator import GenAIPromptGeneratorAgent
from .notification import NotificationAgent
from ..models import ReminderRequest, ReminderResponse, Task
from typing import List
import datetime

class OrchestratorAgent(Agent):
    """
    Coordinates the entire reminder workflow. Delegates tasks to other agents.
    """
    def __init__(self, task_manager: TaskManagerAgent, contextualizer: ContextualizerAgent, 
                 prompt_generator: GenAIPromptGeneratorAgent, notifier: NotificationAgent):
        super().__init__("OrchestratorAgent")
        self.task_manager = task_manager
        self.contextualizer = contextualizer
        self.prompt_generator = prompt_generator
        self.notifier = notifier

    def process_reminder_request(self, reminder_req: ReminderRequest) -> List[ReminderResponse]:
        print(f"[{self.name}] Received reminder request for date: {reminder_req.current_date}")
        responses = []
        
        tasks_to_remind = self.task_manager.get_tasks_due_for_reminder(reminder_req.current_date)

        for task in tasks_to_remind:
            try:
                combined_context = self.contextualizer.gather_context(task)
                subject, message = self.prompt_generator.generate_reminder_prompt(combined_context)
                success = self.notifier.send_reminder(task.assigned_to, subject, message)

                if success:
                    self.task_manager.update_last_reminder_sent(task.task_id, datetime.datetime.now())
                    responses.append(ReminderResponse(task_id=task.task_id, recipient=task.assigned_to, subject=subject, message=message, status="Reminder Sent"))
                else:
                    responses.append(ReminderResponse(task_id=task.task_id, recipient=task.assigned_to, subject=subject, message="", status="Failed to Send Reminder"))
            except Exception as e:
                print(f"[{self.name}] Error processing task {task.task_id}: {e}")
                responses.append(ReminderResponse(task_id=task.task_id, recipient=task.assigned_to, subject="Error", message="", status="Failed", error=str(e)))
        return responses