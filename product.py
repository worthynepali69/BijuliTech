class Product:
    def __init__(self, pid, name, price, stock):
        self.__pid = pid
        self.name = name
        self.price = price
        self.stock = stock

    def update_stock(self, qty):
        if qty < 0:
            raise ValueError("Quantity cannot be negative.")
        self.stock = qty

    def display_info(self):
        return f"{self.name} | ${self.price:.2f} | Stock: {self.stock}"
