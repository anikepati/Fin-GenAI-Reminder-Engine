# cmbs_reminder_system/agents/prompt_generator.py
from .base import Agent
from ..models import CombinedContext
import datetime
import os # To get API key from environment variables

# Import the Google Generative AI SDK
import google.generativeai as genai

class GenAIPromptGeneratorAgent(Agent):
    """
    Leverages a Generative AI model (LLM) to create highly detailed,
    context-aware reminder messages.
    """
    def __init__(self):
        super().__init__("GenAIPromptGeneratorAgent")
        
        # --- Configure Gemini LLM ---
        # It's highly recommended to load your API key from an environment variable
        # For example: export GOOGLE_API_KEY='your_api_key_here'
        GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") 
        if not GEMINI_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it before running.")
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Choose the model. 'gemini-pro' is a good general-purpose text generation model.
        self.llm_model = genai.GenerativeModel('gemini-pro') 
        print(f"[{self.name}] Gemini LLM initialized.")


    def _call_gemini_llm(self, prompt: str) -> str:
        """
        Calls the Gemini LLM API with the given prompt.
        """
        try:
            print(f"[{self.name}] Calling Gemini LLM with prompt (truncated):\n{prompt[:500]}...")
            
            # The actual API call
            response = self.llm_model.generate_content(prompt)
            
            # Extract the text content from the response
            if response.candidates:
                # Assuming the first candidate is the desired response
                return response.candidates[0].content.parts[0].text
            else:
                print(f"[{self.name}] Gemini returned no candidates for the prompt.")
                return "Error: Could not generate reminder message."

        except Exception as e:
            print(f"[{self.name}] Error calling Gemini LLM: {e}")
            return f"Error generating reminder: {e}"

    def generate_reminder_prompt(self, context: CombinedContext) -> tuple[str, str]:
        print(f"[{self.name}] Constructing prompt for task {context.task_context.task_id}...")
        task = context.task_context
        prop = context.property_context
        loan = context.loan_context

        # Construct a comprehensive prompt for the LLM
        llm_prompt = f"""
        You are an AI assistant specialized in CMBS (Commercial Mortgage-Backed Securities) asset management.
        Your goal is to generate a highly detailed, urgent, and actionable follow-up email reminder for an asset manager.
        The reminder should be professional, concise, and guide the user on critical next steps.

        Here are the task details:
        - Task ID: {task.task_id}
        - Description: {task.description}
        - Assigned To: {task.assigned_to}
        - Original Due Date: {task.due_date.strftime('%Y-%m-%d')}
        - Current Date: {datetime.date.today().strftime('%Y-%m-%d')}
        - Status: {task.status}
        - Priority: {task.priority}
        - Task Type: {task.task_type}
        - Property ID: {task.property_id or 'N/A'}
        - Loan ID: {task.loan_id or 'N/A'}
        - Last Update Date: {task.last_update_date.strftime('%Y-%m-%d') if task.last_update_date else 'N/A'}
        - Last Update Notes: {task.last_update_notes or 'None'}
        """

        if task.dependencies:
            llm_prompt += "\nDependent Tasks Status:\n"
            for dep_id, dep_status in task.dependent_tasks_status.items():
                llm_prompt += f"- {dep_id}: {dep_status}\n"

        if prop:
            llm_prompt += f"""
        Property Context:
        - Property Type: {prop.property_type}
        - Current Occupancy: {prop.occupancy_rate*100:.0f}%
        """
        
        if loan:
            llm_prompt += f"""
        Loan Context:
        - Loan Type: {loan.loan_type}
        - Maturity Date: {loan.maturity_date.strftime('%Y-%m-%d')}
        - DSCR Covenant: {loan.dscr_covenant or 'N/A'} (important for financial statements and performance reviews)
        """
        
        if context.market_news_summary:
            llm_prompt += f"""
        Relevant Market Insight:
        - {context.market_news_summary}
        """

        llm_prompt += f"""

        The reminder should:
        - Start with "Subject: " followed by the email subject line, then two newlines, then the email body.
        - Clearly state the current status (e.g., overdue, due soon) and its exact duration (e.g., "overdue by X days").
        - **Emphasize the importance and potential implications** based on task type, property, and loan context (e.g., compliance risks, impact on valuation/surveillance, market trends, covenant breaches).
        - **Reference the last update** and suggest **concrete, actionable next steps** based on the current situation and previous attempts. If dependencies are met, mention that. If the last update notes suggest a blocker, provide advice to overcome it.
        - Maintain a professional, concise, and actionable tone suitable for an internal asset manager.
        - The recipient is {task.assigned_to}.

        Example for an overdue financial statement task:
        Subject: URGENT: Action Required - Overdue Q1 2025 Financial Statements for Grand Tower Office (PROP-GRND)

        Dear [Asset Manager Name],

        This is an urgent follow-up regarding your task **TASK-XXXX: [Description]** for **[Property Name] ([Property ID])**, associated with **Loan [Loan ID]**. The original due date was [Original Due Date], meaning this task is now **overdue by X days**.

        **Criticality & Impact:**
        Timely submission of these financials is paramount. [Explain loan covenant implications, market impact, etc.].

        **Current Status & Immediate Next Steps:**
        Your last update on [Last Update Date] indicated you "[Last Update Notes]". It's been [Days since last update] since your last outreach.

        **Please prioritize the following actions immediately:**
        1. [Concrete step 1]
        2. [Concrete step 2]
        3. [Concrete step 3, e.g., escalation]

        You should have all preliminary information, as dependent tasks like [List completed dependencies] are completed.

        Your prompt action on this overdue and critical item is highly appreciated to maintain loan compliance and ensure accurate portfolio reporting.

        Best regards,

        CMBS Asset Management System
        """

        # Call Gemini LLM
        generated_content = self._call_gemini_llm(llm_prompt)
        
        # Attempt to parse subject and body from LLM output
        subject_line = "Automated Reminder" # Default subject
        body = generated_content

        if "Subject:" in generated_content:
            parts = generated_content.split("Subject:", 1)
            if len(parts) > 1:
                subject_body = parts[1].strip()
                if "\n\n" in subject_body:
                    subject_part, body_part = subject_body.split("\n\n", 1)
                    subject_line = subject_part.strip()
                    body = body_part.strip()
                else:
                    # Fallback if Subject is there but no clear body separation
                    subject_line = subject_body.split('\n')[0].strip()
                    body = subject_body.strip() # Entire text as body if no clear split
                
        # Basic cleanup if LLM includes salutation/sign-off outside of actual body.
        # This part might need fine-tuning based on actual LLM output patterns.
        if body.startswith("Dear"):
            body = body.split('\n', 2)[-1] # Remove salutation
        if "Best regards," in body:
            body = body.split("Best regards,")[0].strip() # Remove sign-off

        print(f"[{self.name}] Prompt generated for task {task.task_id}.")
        return subject_line, body