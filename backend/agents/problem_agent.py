class ProblemAgent:

    def handle(self, command, params):
        """
        Handles:
        problem generate arrays
        problem generate strings
        problem generate loops
        """

        command = command.lower()

        if command.startswith("generate "):
            topic = command.replace("generate ", "")

            response_text = (
                f"Here are simple practice problems for {topic}:\n\n"
                f"1) Basic {topic} problem.\n"
                f"2) Intermediate {topic} logic.\n"
                f"3) One challenge question.\n"
            )

            return {
                "agent": "problem",
                "response": response_text
            }

        return {
            "agent": "problem",
            "error": "Unknown problem command!"
        }
