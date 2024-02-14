import sqlite3
from typing import List
import random
import string
from datetime import datetime



def check_ref_exists(ref: str):
    with sqlite3.connect("atm.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE ref = ?", (ref,))
            count = cursor.fetchone()[0]
            return count > 0

def generate_random_string(length=10):

    characters = string.ascii_letters + string.digits


    while True:
        result = ''.join(random.choice(characters) for _ in range(length))
        
        if not check_ref_exists(result):
            return result



class Bank:
    def __init__(self, bank_name):
        self.bank_name = bank_name


class Transaction:
    def __init__(self, ref, account_number, amount, tx_type, timestamp):
        self.ref = ref
        self.account_number = account_number
        self.amount = amount
        self.tx_type = tx_type
        self.timestamp = timestamp


class Customer:
    def __init__(self, username, pin, name, account_number=None, balance=0):
        self.username = username
        self.pin = pin
        self.name = name
        self.account_number = account_number if account_number else self.generate_account_number()
        self.balance = balance if balance else 0
        self.transactions = []

    def generate_account_number(self):
        """
        Generates one that is unassigned
        """
        while True:
            new_account_number = str(random.randint(10000000, 99999999))

            if not self.account_number_exists(new_account_number):
                return new_account_number
    

    def account_number_exists(self, account_number):
        """
        Checks if the account number already exists in the database
        """
        with sqlite3.connect("atm.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers WHERE account_number = ?", (account_number,))
            count = cursor.fetchone()[0]
            return count > 0
    


    def deposit(self, amount):
        self.balance += amount

        tx = self.create_transaction(amount, tx_type="deposit")
        self.record_transaction(tx)

        return True

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount

            tx = self.create_transaction(amount, tx_type="withdrawal")
            self.record_transaction(tx)

            return True
        else:
            print("Insufficient funds.")
            return False
    

    def transfer(self, amount, account_number):
        if amount >= self.balance:
            print("Insufficient funds")
            return False
        
        else:
            # Deduct amount from user account.
            self.withdraw(amount)

            # Top up recipient account
            Customer(account_number).deposit(amount)

            return True
    
    def create_transaction(self, amount, tx_type):
        ref = generate_random_string()

        tx = Transaction(ref=ref, tx_type=tx_type, amount=amount, account_number=self.account_number, timestamp=datetime.now())

        return tx
    
    def record_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)
    
    def load_transactions(self, transactions: List[Transaction]):
        self.transactions = transactions



class ATM:
    def __init__(self, bank, customers):
        self.bank = bank
        self.balance = 10000 # Set initial balance to 10000
        self.customers = customers

    def authenticate_customer(self, username, pin):
        customer = next((cust for cust in self.customers if cust.username == username), None)
        
        if customer is not None:
            if customer.pin == pin:
                return True, "Valid Credentials"
            else:
                # Raise an exception when authentication fails
                return False, "Invalid PIN"
        
        else:
            return False, "New Customer"

    def create_customer(self, username, pin, name):
        new_customer = Customer(username, pin, name)
        self.customers.append(new_customer)
        return new_customer
    
    def check_balance(self, customer):
        return customer.balance

    def deposit_funds(self, customer, amount):
        return customer.deposit(amount)

    def withdraw_cash(self, customer: Customer, amount):
        
        # Check if amount is less than balance
        try:
            if int(amount) > self.balance:
                return False, "Temporarily unable to dispense funds"
        except ValueError:
            return False, "Invalid input"
        
        self.balance -= amount
        return True, customer.withdraw(amount)

def load_customers_from_database():
    customers = []
    with sqlite3.connect("atm.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                username TEXT PRIMARY KEY,
                pin TEXT,
                name TEXT,
                account_number TEXT,
                balance REAL
            )
        """)
        cursor.execute("SELECT username, pin, name, account_number, balance FROM customers")
        rows = cursor.fetchall()
        for row in rows:
            customers.append(Customer(*row))
        
    return customers


def load_customer_transactions(customer: Customer):
    transactions = []

    with sqlite3.connect("atm.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""

            CREATE TABLE IF NOT EXISTS transactions (
                ref TEXT PRIMARY KEY,
                account_number TEXT,
                amount TEXT,
                tx_type TEXT,
                timestamp TIMESTAMP
            )
        """)

        cursor.execute(f"SELECT * FROM transactions WHERE account_number={customer.account_number}")

        rows = cursor.fetchall()

        for row in rows:
            transactions.append(Transaction(*row))
        
    return transactions

class Technician:
    def perform_maintenance(self, atm):
        # Placeholder for maintenance actions
        print("Technician performing maintenance on the ATM.")

    def perform_repairs(self, atm):
        # Placeholder for repair actions
        print("Technician performing repairs on the ATM.")
    
    def check_balance(self, atm):
        return atm.balance

    def replenish_cash(self, atm: ATM, amount: int) -> None:
        # Placeholder for cash replenishment actions
        print(f"Technician replenishing ATM with ${amount}.")
        try:
            atm.balance += int(amount)
        except ValueError:
            print("Invalid amount")        

    def upgrade_hardware(self, atm):
        # Placeholder for hardware upgrade actions
        print("Technician upgrading hardware on the ATM.")

    def upgrade_firmware(self, atm):
        # Placeholder for firmware upgrade actions
        print("Technician upgrading firmware on the ATM.")

def technician_operations(atm: ATM, technician: Technician):
    print("\nTechnician Operations:")
    print("1 - Perform Maintenance \t 2 - Perform Repairs \t 3 - View Cash Balance \t 4 - Replenish Cash \t 5 - Upgrade Hardware \t 6 - Upgrade Firmware")

    operation = input("\nEnter technician operation (1-5): ")

    if operation == "1":
        technician.perform_maintenance(atm)
    elif operation == "2":
        technician.perform_repairs(atm)
    elif operation == "3":
        print('ATM Balance: \n')
        print("$" + str(technician.check_balance(atm)))
    elif operation == "4":
        amount = float(input("Enter amount to replenish: "))
        technician.replenish_cash(atm, amount)
    elif operation == "5":
        technician.upgrade_hardware(atm)
    elif operation == "6":
        technician.upgrade_firmware(atm)
    else:
        print("Invalid technician operation. Try again.")




def main():
    bank = Bank("Example Bank")
    customers = load_customers_from_database()
    atm = ATM(bank, customers)
    technician = Technician()

    username = input("Enter Your Username: ")
    pin = input("Enter Your PIN: ")
    name = input("Enter Your Full Name: ")

    auth_status, msg = atm.authenticate_customer(username, pin)

    while not auth_status and msg == "Invalid PIN":
        print("Invalid Pin\n\n")
        pin = input("Retry PIN: ")
        auth_status, msg = atm.authenticate_customer(username, pin)

    if auth_status:
        print("Logging in...")
        customer = next(cust for cust in customers if cust.username == username)
    else:
        customer = atm.create_customer(username, pin, name)
        print(f"New customer account created for {customer.username}")

    transactions = load_customer_transactions(customer)
    customer.transactions = transactions

    while True:
        print(f"\nWelcome {customer.name}! \n1 - Check Balance \t 2 - Deposit Funds \t 3 - Withdraw Cash \t 4 - View Transaction History \t 5 - Technician Operations \t 6 - Quit ")

        selection = input("\nEnter your selection (1-5): ")

        if selection == "1":
            balance = atm.check_balance(customer)
            print("Customer Account Number:", customer.account_number)
            print("Customer Name:", customer.name)
            print("Your Balance is:", balance)
        elif selection == "2":
            amount = float(input("Enter amount to deposit: "))
            success = atm.deposit_funds(customer, amount)
            if success:
                print("Deposit successfully. New Balance is:", customer.balance)
        elif selection == "3":
            try:
                amount = float(input("Enter amount to withdraw: "))
            except ValueError:
                print("Invalid amount")

            success, status = atm.withdraw_cash(customer, amount)

            

            if success:
                if str(type(status)) == "<class 'bool'>":
                    # Check if the customer.withdraw() method did not return False.
                    if status:
                        print("Withdrawal successful. Updated Balance:", customer.balance)
            else:
                print(status)
        elif selection == "4":
            print("\n\nRecent Transactions")
            for tx in customer.transactions[:10]:
                print(f"{tx.timestamp} --> ${tx.amount} | {tx.tx_type} | {tx.ref}\n")
        elif selection == "5":
            technician_operations(atm, technician)
        elif selection == "6":
            print("Thank you for using our ATM.")

            with sqlite3.connect("atm.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?)",
                               (customer.username, customer.pin, customer.name, customer.account_number, customer.balance))
                

                for tx in customer.transactions:
                    cursor.execute("INSERT OR REPLACE INTO transactions VALUES (?, ?, ?, ?, ?)", (tx.ref, tx.account_number, tx.amount, tx.tx_type, tx.timestamp))
                    
                conn.commit()
            exit()
        else:
            print("Invalid selection. Try again.")

if __name__ == "__main__":
    main()