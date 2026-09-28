class FileAgent:

    def handle(self, command, params):
        """
        Handles:
        file:structure python project
        file:structure c project
        """

        command = command.lower()

        if command.startswith("structure "):
            topic = command.replace("structure ", "")

            if topic == "python project":
                structure = (
                    "Python Project Structure:\n"
                    "project/\n"
                    " ├── main.py\n"
                    " ├── utils/\n"
                    " ├── data/\n"
                    " └── requirements.txt\n"
                )
                return {"agent": "file", "response": structure}

            if topic == "c project":
                structure = (
                    "C Project Structure:\n"
                    "project/\n"
                    " ├── main.c\n"
                    " ├── include/\n"
                    " ├── src/\n"
                    " └── Makefile\n"
                )
                return {"agent": "file", "response": structure}

            return {"agent": "file", "response": "Unknown structure type!"}

        return {
            "agent": "file",
            "response": "Unknown file command!"
        }
