class player:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.team = None  # "X" | "Y" | None

    def __str__(self):
        return f"Name: {self.name}, ID: {self.id}, Team: {self.team}"
