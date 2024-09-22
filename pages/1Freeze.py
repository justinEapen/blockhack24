import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

class EnhancedZKProof:
    @staticmethod
    def generate_keys():
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def generate_proof(private_key, public):
        signature = private_key.sign(
            public.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    @staticmethod
    def verify_proof(public_key, signature, public):
        try:
            public_key.verify(
                signature,
                public.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

class EthereumAccount:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance
        self.frozen_balance = 0
        self.nonce = 0
        self.transactions = []
        self.private_key, self.public_key = EnhancedZKProof.generate_keys()

    def add_transaction(self, amount, description, to_address, is_frozen=False, purpose=None):
        if is_frozen:
            self.frozen_balance += amount
        else:
            self.balance += amount
        self.nonce += 1
        tx_hash = hashlib.sha256(f"{self.nonce}{amount}{to_address}".encode()).hexdigest()
        self.transactions.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'amount': amount,
            'description': description,
            'balance': self.balance,
            'frozen_balance': self.frozen_balance,
            'tx_hash': tx_hash,
            'purpose': purpose
        })
        return tx_hash

class EthereumScholarshipSystem:
    def __init__(self):
        self.accounts = {
            'Admin': EthereumAccount('Admin', 1000000),
            'Student1': EthereumAccount('Student1'),
            'Student2': EthereumAccount('Student2'),
            'Vendor1': EthereumAccount('Vendor1'),
            'Vendor2': EthereumAccount('Vendor2')
        }
        self.zkp = EnhancedZKProof()
        self.approved_vendors = {'Vendor1', 'Vendor2'}
        self.educational_purposes = {'Tuition', 'Books', 'School Supplies', 'Accommodation'}
        self.disallowed_purposes = {'Buy Alcohol', 'Buy Cigarette', 'Buy to Watch Non-Educational'}
        self.spending_limits = {'Tuition': 10000, 'Books': 1000, 'School Supplies': 500, 'Accommodation': 5000}

    def issue_scholarship(self, student, amount):
        if self.accounts['Admin'].balance >= amount:
            tx_hash = self.accounts['Admin'].add_transaction(-amount, f"Issue scholarship to {student}", student)
            self.accounts[student].add_transaction(amount, "Receive scholarship", 'Admin', is_frozen=True)
            return tx_hash
        return None

    def spend_scholarship(self, student, vendor, amount, purpose):
        if vendor not in self.approved_vendors:
            return None, None, "Vendor not approved for educational expenses"
        
        if purpose in self.disallowed_purposes:
            return None, None, f"Spending on '{purpose}' is not allowed."

        if purpose not in self.educational_purposes:
            return None, None, "Purpose is not educational"

        if amount > self.spending_limits.get(purpose, 0):
            return None, None, f"Amount exceeds spending limit for {purpose}"

        public = f"{student}{vendor}{amount}{purpose}"
        proof = self.zkp.generate_proof(self.accounts[student].private_key, public)

        if self.zkp.verify_proof(self.accounts[student].public_key, proof, public) and self.accounts[student].frozen_balance >= amount:
            tx_hash_student = self.accounts[student].add_transaction(-amount, f"Spend at {vendor}", vendor, is_frozen=True, purpose=purpose)
            tx_hash_vendor = self.accounts[vendor].add_transaction(amount, f"Receive from {student}", student, purpose=purpose)
            return tx_hash_student, proof, "Transaction successful"
        return None, None, "Insufficient frozen funds or invalid proof"

    def get_all_transactions(self):
        all_transactions = []
        for account in self.accounts.values():
            all_transactions.extend(account.transactions)
        return sorted(all_transactions, key=lambda x: x['timestamp'], reverse=True)

    def transfer_scholarship(self, from_student, to_student, amount):
        if self.accounts[from_student].frozen_balance >= amount:
            tx_hash_from = self.accounts[from_student].add_transaction(-amount, f"Transfer to {to_student}", to_student, is_frozen=True)
            tx_hash_to = self.accounts[to_student].add_transaction(amount, f"Receive from {from_student}", from_student, is_frozen=True)
            return tx_hash_from
        return None

def main():
    st.title("Ethcash")

    if 'system' not in st.session_state:
        st.session_state.system = EthereumScholarshipSystem()

    system = st.session_state.system

    st.sidebar.header("Actions")
    action = st.sidebar.selectbox("Choose an action", ["View Balances", "Issue Scholarship", "Spend Scholarship", "Transfer Scholarship", "Admin View"])

    if action == "View Balances":
        st.header("Account Balances")
        balances = {name: f"Regular: {account.balance}, Frozen: {account.frozen_balance}" 
                    for name, account in system.accounts.items()}
        st.table(pd.DataFrame(list(balances.items()), columns=["Account", "Balance"]))

    elif action == "Issue Scholarship":
        st.header("Issue Scholarship")
        student = st.selectbox("Select Student", ["Student1", "Student2"])
        amount = st.number_input("Amount", min_value=1, max_value=system.accounts['Admin'].balance)
        if st.button("Issue Scholarship"):
            tx_hash = system.issue_scholarship(student, amount)
            if tx_hash:
                st.success(f"Successfully issued {amount} to {student} as frozen funds. Transaction Hash: {tx_hash}")
            else:
                st.error("Failed to issue scholarship. Insufficient admin funds.")

    elif action == "Spend Scholarship":
        st.header("Spend Scholarship")
        student = st.selectbox("Select Student", ["Student1", "Student2"])
        vendor = st.selectbox("Select Vendor", ["Vendor1", "Vendor2"])
        purpose = st.selectbox("Select Purpose", list(system.educational_purposes) + list(system.disallowed_purposes))
        max_amount = min(system.accounts[student].frozen_balance, system.spending_limits.get(purpose, system.accounts[student].frozen_balance))
        amount = st.number_input("Amount", min_value=1, max_value=max_amount) if max_amount > 0 else 0

        if st.button("Spend Scholarship"):
            tx_hash, proof, message = system.spend_scholarship(student, vendor, amount, purpose)
            if tx_hash:
                st.success(f"Successfully spent {amount} from {student} to {vendor} for {purpose}. Transaction Hash: {tx_hash}")
                st.info(f"Zero-Knowledge Proof: {proof}")
            else:
                st.error(f"Failed to spend scholarship. {message}")

    elif action == "Transfer Scholarship":
        st.header("Transfer Scholarship")
        from_student = st.selectbox("From Student", ["Student1", "Student2"])
        to_student = st.selectbox("To Student", [s for s in ["Student1", "Student2"] if s != from_student])
        max_amount = system.accounts[from_student].frozen_balance
        amount = st.number_input("Amount", min_value=1, max_value=max_amount) if max_amount > 0 else 0

        if st.button("Transfer Scholarship"):
            tx_hash = system.transfer_scholarship(from_student, to_student, amount)
            if tx_hash:
                st.success(f"Successfully transferred {amount} from {from_student} to {to_student}. Transaction Hash: {tx_hash}")
            else:
                st.error("Failed to transfer scholarship. Insufficient funds.")

    elif action == "Admin View":
        st.header("Admin View - All Transactions")
        all_transactions = system.get_all_transactions()
        st.table(pd.DataFrame(all_transactions))

    st.header("Transaction History")
    account = st.selectbox("Select Account", list(system.accounts.keys()))
    st.table(pd.DataFrame(system.accounts[account].transactions))

if __name__ == "__main__":
    main()
