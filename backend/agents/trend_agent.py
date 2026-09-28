class TrendAgent:

    def handle(self, command, params):
        """
        Handles:
        trend:tech
        trend:ai
        trend:programming
        """

        topic = command.lower()

        fake_trends = {
            "tech": [
                "AI automation",
                "Quantum computing",
                "Cybersecurity upgrades"
            ],
            "ai": [
                "LLMs improving rapidly",
                "AI agents everywhere",
                "Multi-modal models trending"
            ],
            "programming": [
                "Python still dominant",
                "Rust rising",
                "Backend → FastAPI popularity"
            ]
        }

        if topic in fake_trends:
            text = f"Top trends in {topic}:\n"
            for t in fake_trends[topic]:
                text += f"- {t}\n"

            return {"agent": "trend", "response": text}

        return {
            "agent": "trend",
            "response": "No trends found for this topic!"
        }
