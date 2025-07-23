# cmbs_reminder_system/agents/task_manager.py
from .base import Agent, r
from ..models import Task, ReminderRequest
import datetime
from typing import List, Optional, Any

class TaskManagerAgent(Agent):
    """
    Manages task data (CRUD operations) and handles task persistence in Redis.
    Also responsible for identifying tasks due for a reminder.
    """
    def __init__(self):
        super().__init__("TaskManagerAgent")
        self._next_task_id_key = "next_task_id"
        if not r.exists(self._next_task_id_key):
            r.set(self._next_task_id_key, 1)

    def add_task(self, task_data: dict) -> Task:
        task_id_int = r.incr(self._next_task_id_key)
        task_data['task_id'] = f"TASK-{task_id_int:04d}"
        task = Task(**task_data)
        self._save_to_redis('task', task)
        print(f"[{self.name}] Task added: {task.task_id} - {task.description}")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._load_from_redis('task', task_id, Task)

    def update_task_status(self, task_id: str, new_status: str, notes: Optional[str] = None) -> Optional[Task]:
        updates = {
            'status': new_status,
            'last_update_date': datetime.date.today().isoformat(),
            'last_update_notes': notes
        }
        if self._update_in_redis('task', task_id, updates):
            return self.get_task(task_id)
        return None
    
    def update_last_reminder_sent(self, task_id: str, timestamp: datetime.datetime) -> Optional[Task]:
        updates = {'last_reminder_sent': timestamp.isoformat()}
        if self._update_in_redis('task', task_id, updates):
            return self.get_task(task_id)
        return None

    def get_tasks_due_for_reminder(self, current_date: datetime.date, reminder_interval_hours: int = 24, due_soon_threshold_days: int = 7) -> List[Task]:
        print(f"[{self.name}] Checking for tasks due for reminder on {current_date}...")
        all_task_keys = r.keys(self._get_redis_key('task', '*'))
        tasks_to_remind: List[Task] = []
        
        for key in all_task_keys:
            task = self.get_task(key.split(':')[1])
            if not task or task.status not in ["Pending", "In Progress"]:
                continue

            send_reminder_now = False
            current_datetime = datetime.datetime.combine(current_date, datetime.datetime.min.time())

            if task.due_date == current_date:
                if not task.last_reminder_sent or task.last_reminder_sent.date() < current_date:
                    send_reminder_now = True
            elif task.due_date < current_date:
                if not task.last_reminder_sent or (current_datetime - task.last_reminder_sent).total_seconds() / 3600 >= reminder_interval_hours:
                    send_reminder_now = True
            elif 0 < (task.due_date - current_date).days <= due_soon_threshold_days:
                 if not task.last_reminder_sent or task.last_reminder_sent.date() < current_date:
                    send_reminder_now = True

            if send_reminder_now:
                dependent_statuses = {}
                for dep_task_id in task.dependencies:
                    dep_task = self.get_task(dep_task_id)
                    dependent_statuses[dep_task_id] = dep_task.status if dep_task else "Not Found"
                task.dependent_tasks_status = dependent_statuses
                tasks_to_remind.append(task)
        
        print(f"[{self.name}] Found {len(tasks_to_remind)} tasks requiring reminders.")
        return tasks_to_remind