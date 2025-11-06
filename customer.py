class Customer:
    def __init__(self, cid, name, phone, points=0):
        self.__cid = cid
        self.name = name
        self.phone = phone
        self.points = points

    def add_points(self, amount):
        self.points += amount // 10  # 1 point per $10 spent

    def display(self):
        return f"{self.name} ({self.phone}) - Points: {self.points}"
