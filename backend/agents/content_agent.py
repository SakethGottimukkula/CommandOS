class ContentAgent:

    def handle(self, command, params):
        """
        Handles:
        content:caption python
        content:caption arrays
        content:caption study tips
        """

        command = command.lower()

        # caption generator
        if command.startswith("caption "):
            topic = command.replace("caption ", "")

            caption = (
                f"📌 Quick take on {topic.title()}:\n"
                f"• Learn the basics first\n"
                f"• Practice small examples\n"
                f"• Build something simple\n"
                f"#learning #{topic.replace(' ', '')}"
            )

            return {"agent": "content", "response": caption}

        return {
            "agent": "content",
            "response": "Unknown content command!"
        }
