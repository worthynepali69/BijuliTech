from models.product import Product
from models.customer import Customer

class Sale:
    def __init__(self, sale_id, customer, product, qty, staff):
        self.sale_id = sale_id
        self.customer = customer
        self.product = product
        self.qty = qty
        self.staff = staff

    def calculate_total(self):
        return self.product.price * self.qty

    def process_sale(self):
        if self.product.stock < self.qty:
            raise Exception("Not enough stock!")
        self.product.stock -= self.qty
        self.customer.add_points(self.calculate_total())
        return f"Processed by {self.staff}: {self.qty} × {self.product.name} → ${self.calculate_total():.2f}"
