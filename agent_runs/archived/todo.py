class TODO:
    def __init__(self, task, completed=False):
        self.task = task
        self.completed = completed

    def mark_complete(self):
        self.completed = True

    def __repr__(self):
        status = 'Done' if self.completed else 'Pending'
        return f"<TODO: {self.task} [{status}]>"