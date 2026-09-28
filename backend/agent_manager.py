from agents.study_agent import StudyAgent
from agents.problem_agent import ProblemAgent
from agents.task_agent import TaskAgent
from agents.file_agent import FileAgent
from agents.trend_agent import TrendAgent
from agents.content_agent import ContentAgent

class AgentManager:

    def __init__(self):
        self.study = StudyAgent()
        self.problem = ProblemAgent()
        self.task = TaskAgent()
        self.file = FileAgent()
        self.trend = TrendAgent()
        self.content = ContentAgent()

    def route(self, user_id, command, params):
        """
        Decides which agent handles the command.
        Expected format: category:action details
        Example: study:explain arrays
        """
        try:
            prefix, actual = command.split(":", 1)
        except ValueError:
            return {"agent": "system", "error": "Invalid command format!"}

        prefix = prefix.lower().strip()
        actual = actual.strip()

        if prefix == "study":
            return self.study.handle(actual, params)

        if prefix == "problem":
            return self.problem.handle(actual, params)

        if prefix == "task":
            return self.task.handle(actual, params)

        if prefix == "file":
            return self.file.handle(actual, params)

        if prefix == "trend":
            return self.trend.handle(actual, params)

        if prefix == "content":
            return self.content.handle(actual, params)

        return {"agent": "system", "error": "Unknown agent prefix!"}


# Export a default manager instance
agent_manager = AgentManager()
