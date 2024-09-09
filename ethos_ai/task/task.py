class Task:
    def __init__(self, task_type):
        self.type = task_type
        # Add any additional attributes needed for the task

    def __str__(self):
        return str(self.type.name)

    def __repr__(self):
        return str(self.type.name)

    def get_type(self):
        return self.type
