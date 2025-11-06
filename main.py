from models.product import Product
from models.customer import Customer
from models.sale import Sale

def main():
    prod = Product(1, "Keyboard", 49.99, 10)
    cust = Customer(1, "Alex", "0211234567")
    sale = Sale(101, cust, prod, 2, "Aayush")

    print(sale.process_sale())
    print(cust.display())
    print(prod.display_info())

if __name__ == "__main__":
    main()
