# cmbs_reminder_system/agents/contextualizer.py
from .base import Agent, r
from ..models import Task, PropertyContext, LoanContext, CombinedContext
import datetime

class ContextualizerAgent(Agent):
    """
    Gathers and synthesizes all relevant context for a task from various sources.
    """
    def __init__(self):
        super().__init__("ContextualizerAgent")
        self._populate_dummy_data()

    def _populate_dummy_data(self):
        prop_grnd = PropertyContext(property_id="PROP-GRND", property_type="Office", occupancy_rate=0.85, square_footage=150000)
        prop_retail = PropertyContext(property_id="PROP-RETAIL", property_type="Retail", occupancy_rate=0.92, square_footage=80000)
        self._save_to_redis('property', prop_grnd)
        self._save_to_redis('property', prop_retail)

        loan_gwr_001 = LoanContext(loan_id="LOAN-GWR-001", loan_type="CMBS", maturity_date=datetime.date(2030, 6, 30), dscr_covenant=1.25)
        loan_rt_002 = LoanContext(loan_id="LOAN-RT-002", loan_type="Bridge", maturity_date=datetime.date(2027, 1, 15), dscr_covenant=1.10)
        self._save_to_redis('loan', loan_gwr_001)
        self._save_to_redis('loan', loan_rt_002)
        print(f"[{self.name}] Dummy property and loan data populated in Redis.")

    def gather_context(self, task: Task) -> CombinedContext:
        print(f"[{self.name}] Gathering context for task {task.task_id}...")
        
        property_context: Optional[PropertyContext] = None
        loan_context: Optional[LoanContext] = None
        market_news_summary: Optional[str] = None

        if task.property_id:
            property_context = self._load_from_redis('property', task.property_id, PropertyContext)
        
        if task.loan_id:
            loan_context = self._load_from_redis('loan', task.loan_id, LoanContext)
        
        if property_context and property_context.property_type == "Office":
             market_news_summary = "Recent reports indicate rising office vacancies in downtown areas, impacting rent growth potential."
        elif property_context and property_context.property_type == "Retail":
             market_news_summary = "Retail sector showing resilience with increased foot traffic in suburban malls."

        combined_context = CombinedContext(
            task_context=task,
            property_context=property_context,
            loan_context=loan_context,
            market_news_summary=market_news_summary
        )
        print(f"[{self.name}] Context gathered for task {task.task_id}.")
        return combined_context