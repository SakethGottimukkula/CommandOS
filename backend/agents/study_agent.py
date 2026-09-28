class StudyAgent:

    def handle(self, command, params):
        """
        Handles commands like:
        study:explain arrays
        study:notes oop
        study:quiz loops
        """
        command = command.lower()

        # Explain topic
        if command.startswith("explain "):
            topic = command.replace("explain ", "")
            return {
                "agent": "study",
                "response": f"Here is a simple explanation of {topic}:\n\n"
                            f"- {topic.title()} is an important concept.\n"
                            f"- Understand the basics first.\n"
                            f"- Practice problems will help you master it."
            }

        # Notes
        if command.startswith("notes "):
            topic = command.replace("notes ", "")
            return {
                "agent": "study",
                "response": f"Here are notes for {topic}:\n\n"
                            f"1) Introduction to {topic}\n"
                            f"2) Important definitions\n"
                            f"3) Example problems\n"
                            f"4) Summary points"
            }

        # Quiz
        if command.startswith("quiz "):
            topic = command.replace("quiz ", "")
            return {
                "agent": "study",
                "response": f"Quick quiz on {topic}:\n"
                            f"1) What is {topic}?\n"
                            f"2) Why is it used?\n"
                            f"3) Give an example."
            }

        return {
            "agent": "study",
            "error": "Unknown study command!"
        }
