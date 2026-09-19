from datetime import datetime, timezone as dt_timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from audit.models import AuditLog
from banking.models import Account, AccountType, Beneficiary, Branch, Card
from loans.models import Loan, LoanPayment
from notifications.models import Notification
from transactions.models import JournalEntry, Transaction, TransactionType
from users.models import Customer, Employee, Role


User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with realistic sample banking data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing sample data before inserting a fresh dataset.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.reset_data()

        with transaction.atomic():
            data = self.seed_data()

        self.stdout.write(self.style.SUCCESS("Sample banking data is ready."))
        self.stdout.write(
            self.style.SUCCESS(
                "Created or updated: "
                f"{len(data['roles'])} roles, "
                f"{len(data['branches'])} branches, "
                f"{len(data['customers'])} customers, "
                f"{len(data['accounts'])} accounts, "
                f"{len(data['transactions'])} transactions."
            )
        )

    def reset_data(self):
        for model in [
            JournalEntry,
            LoanPayment,
            Notification,
            AuditLog,
            Card,
            Beneficiary,
            Loan,
            Transaction,
            Account,
            Employee,
            Customer,
            User,
            Role,
            TransactionType,
            AccountType,
            Branch,
        ]:
            model.objects.all().delete()

    def seed_data(self):
        roles = {
            name: self.get_role(name)
            for name in ["Admin", "Manager", "Teller", "Auditor", "Customer", "System"]
        }

        branches = {
            "downtown": self.get_branch("BR001", "Downtown Branch", "100 Main St", "New York"),
            "uptown": self.get_branch("BR002", "Uptown Branch", "250 North Ave", "Chicago"),
            "riverside": self.get_branch("BR003", "Riverside Branch", "88 River Rd", "Los Angeles"),
        }

        account_types = {
            "savings": self.get_account_type("Savings", Decimal("3.50"), "Primary savings account"),
            "checking": self.get_account_type("Checking", Decimal("1.25"), "Daily spending account"),
            "salary": self.get_account_type("Salary", Decimal("0.75"), "Payroll account"),
        }

        admin = self.get_user(
            username="admin1",
            password="Admin@12345",
            role=roles["Admin"],
            status="ACTIVE",
            first_name="System",
            last_name="Admin",
            email="admin1@bank.local",
            is_staff=True,
            is_superuser=True,
        )

        manager = self.get_user(
            username="manager1",
            password="Manager@12345",
            role=roles["Manager"],
            status="ACTIVE",
            first_name="Maya",
            last_name="Patel",
            email="maya.patel@bank.local",
        )

        teller = self.get_user(
            username="teller1",
            password="Teller@12345",
            role=roles["Teller"],
            status="ACTIVE",
            first_name="Noah",
            last_name="Reed",
            email="noah.reed@bank.local",
        )

        auditor = self.get_user(
            username="auditor1",
            password="Auditor@12345",
            role=roles["Auditor"],
            status="ACTIVE",
            first_name="Ivy",
            last_name="Stone",
            email="ivy.stone@bank.local",
        )

        system_user = self.get_user(
            username="bank_system",
            password="System@12345",
            role=roles["System"],
            status="ACTIVE",
            first_name="Bank",
            last_name="System",
            email="system@bank.local",
        )

        customer_specs = [
            {
                "username": "alice.johnson",
                "password": "Customer@12345",
                "first_name": "Alice",
                "last_name": "Johnson",
                "email": "alice.johnson@example.com",
                "national_id": "NID-1001",
                "branch": branches["downtown"],
            },
            {
                "username": "bob.smith",
                "password": "Customer@12345",
                "first_name": "Bob",
                "last_name": "Smith",
                "email": "bob.smith@example.com",
                "national_id": "NID-1002",
                "branch": branches["uptown"],
            },
            {
                "username": "carol.garcia",
                "password": "Customer@12345",
                "first_name": "Carol",
                "last_name": "Garcia",
                "email": "carol.garcia@example.com",
                "national_id": "NID-1003",
                "branch": branches["riverside"],
            },
            {
                "username": "david.lee",
                "password": "Customer@12345",
                "first_name": "David",
                "last_name": "Lee",
                "email": "david.lee@example.com",
                "national_id": "NID-1004",
                "branch": branches["downtown"],
            },
            {
                "username": "emma.davis",
                "password": "Customer@12345",
                "first_name": "Emma",
                "last_name": "Davis",
                "email": "emma.davis@example.com",
                "national_id": "NID-1005",
                "branch": branches["uptown"],
            },
            {
                "username": "frank.moore",
                "password": "Customer@12345",
                "first_name": "Frank",
                "last_name": "Moore",
                "email": "frank.moore@example.com",
                "national_id": "NID-1006",
                "branch": branches["riverside"],
            },
        ]

        customers = {}
        for spec in customer_specs:
            user = self.get_user(
                username=spec["username"],
                password=spec["password"],
                role=roles["Customer"],
                status="ACTIVE",
                first_name=spec["first_name"],
                last_name=spec["last_name"],
                email=spec["email"],
            )
            customer = self.get_customer(user, spec["national_id"])
            customers[spec["username"]] = customer

        employees = {
            "manager1": self.get_employee(manager, branches["downtown"], "Branch Manager"),
            "teller1": self.get_employee(teller, branches["uptown"], "Senior Teller"),
            "auditor1": self.get_employee(auditor, branches["riverside"], "Internal Auditor"),
        }

        system_customer = self.get_customer(system_user, "SYS-0000")

        accounts = {
            "system": self.get_account(
                customer=system_customer,
                branch=branches["downtown"],
                account_type=account_types["checking"],
                account_number="1000000001",
                ledger_balance=Decimal("250000.00"),
                available_balance=Decimal("250000.00"),
                status="ACTIVE",
                opened_at=self.dt(2025, 1, 2, 9, 0),
            ),
            "alice_checking": self.get_account(
                customer=customers["alice.johnson"],
                branch=branches["downtown"],
                account_type=account_types["checking"],
                account_number="2000000001",
                ledger_balance=Decimal("5840.00"),
                available_balance=Decimal("5785.00"),
                status="ACTIVE",
                opened_at=self.dt(2025, 2, 12, 10, 30),
            ),
            "alice_savings": self.get_account(
                customer=customers["alice.johnson"],
                branch=branches["downtown"],
                account_type=account_types["savings"],
                account_number="2000000002",
                ledger_balance=Decimal("18250.00"),
                available_balance=Decimal("18250.00"),
                status="ACTIVE",
                opened_at=self.dt(2025, 2, 12, 10, 45),
            ),
            "bob_checking": self.get_account(
                customer=customers["bob.smith"],
                branch=branches["uptown"],
                account_type=account_types["checking"],
                account_number="2000000003",
                ledger_balance=Decimal("7345.00"),
                available_balance=Decimal("7220.00"),
                status="ACTIVE",
                opened_at=self.dt(2025, 3, 1, 11, 0),
            ),
            "carol_savings": self.get_account(
                customer=customers["carol.garcia"],
                branch=branches["riverside"],
                account_type=account_types["savings"],
                account_number="2000000004",
                ledger_balance=Decimal("12680.00"),
                available_balance=Decimal("12680.00"),
                status="ACTIVE",
                opened_at=self.dt(2025, 3, 8, 9, 15),
            ),
            "david_salary": self.get_account(
                customer=customers["david.lee"],
                branch=branches["downtown"],
                account_type=account_types["salary"],
                account_number="2000000005",
                ledger_balance=Decimal("9150.00"),
                available_balance=Decimal("9150.00"),
                status="ACTIVE",
                opened_at=self.dt(2025, 4, 2, 8, 0),
            ),
            "david_checking": self.get_account(
                customer=customers["david.lee"],
                branch=branches["downtown"],
                account_type=account_types["checking"],
                account_number="2000000006",
                ledger_balance=Decimal("2410.00"),
                available_balance=Decimal("2410.00"),
                status="ACTIVE",
                opened_at=self.dt(2025, 4, 2, 8, 15),
            ),
            "emma_savings": self.get_account(
                customer=customers["emma.davis"],
                branch=branches["uptown"],
                account_type=account_types["savings"],
                account_number="2000000007",
                ledger_balance=Decimal("15920.00"),
                available_balance=Decimal("15420.00"),
                status="ACTIVE",
                opened_at=self.dt(2025, 4, 18, 13, 0),
            ),
            "frank_checking": self.get_account(
                customer=customers["frank.moore"],
                branch=branches["riverside"],
                account_type=account_types["checking"],
                account_number="2000000008",
                ledger_balance=Decimal("4025.00"),
                available_balance=Decimal("4025.00"),
                status="ACTIVE",
                opened_at=self.dt(2025, 5, 9, 12, 0),
            ),
        }

        cards = [
            self.get_card(
                accounts["alice_checking"],
                "4000000000000001",
                "DEBIT",
                self.dt_date(2028, 5, 31),
                "123",
                "ACTIVE",
            ),
            self.get_card(
                accounts["alice_savings"],
                "4000000000000002",
                "ATM",
                self.dt_date(2027, 11, 30),
                "124",
                "ACTIVE",
            ),
            self.get_card(
                accounts["bob_checking"],
                "4000000000000003",
                "DEBIT",
                self.dt_date(2025, 12, 31),
                "125",
                "EXPIRED",
            ),
            self.get_card(
                accounts["carol_savings"],
                "4000000000000004",
                "DEBIT",
                self.dt_date(2028, 8, 31),
                "126",
                "ACTIVE",
            ),
            self.get_card(
                accounts["david_salary"],
                "4000000000000005",
                "ATM",
                self.dt_date(2029, 2, 28),
                "127",
                "ACTIVE",
            ),
            self.get_card(
                accounts["david_checking"],
                "4000000000000006",
                "DEBIT",
                self.dt_date(2028, 2, 28),
                "128",
                "BLOCKED",
            ),
            self.get_card(
                accounts["emma_savings"],
                "4000000000000007",
                "DEBIT",
                self.dt_date(2027, 9, 30),
                "129",
                "ACTIVE",
            ),
            self.get_card(
                accounts["frank_checking"],
                "4000000000000008",
                "ATM",
                self.dt_date(2029, 12, 31),
                "130",
                "ACTIVE",
            ),
        ]

        beneficiaries = [
            self.get_beneficiary(
                customers["alice.johnson"],
                "Carol Garcia",
                "2000000004",
                "Riverside Bank",
                "Carol savings",
            ),
            self.get_beneficiary(
                customers["alice.johnson"],
                "Frank Moore",
                "2000000008",
                "Riverside Bank",
                "Frank checking",
            ),
            self.get_beneficiary(
                customers["bob.smith"],
                "Alice Johnson",
                "2000000001",
                "Downtown Bank",
                "Alice checking",
            ),
            self.get_beneficiary(
                customers["carol.garcia"],
                "Bob Smith",
                "2000000003",
                "Uptown Bank",
                "Bob checking",
            ),
            self.get_beneficiary(
                customers["david.lee"],
                "Emma Davis",
                "2000000007",
                "Uptown Bank",
                "Emma savings",
            ),
            self.get_beneficiary(
                customers["emma.davis"],
                "David Lee",
                "2000000006",
                "Downtown Bank",
                "David checking",
            ),
            self.get_beneficiary(
                customers["frank.moore"],
                "Alice Johnson",
                "2000000002",
                "Downtown Bank",
                "Alice savings",
            ),
        ]

        transaction_types = {
            "deposit": self.get_transaction_type("Deposit", "Cash or external deposit"),
            "withdrawal": self.get_transaction_type("Withdrawal", "Cash withdrawal"),
            "transfer": self.get_transaction_type("Transfer", "Internal account transfer"),
            "loan_repayment": self.get_transaction_type("Loan Repayment", "Repayment against an active loan"),
            "loan_disbursement": self.get_transaction_type("Loan Disbursement", "Loan funds released to customer"),
            "fee": self.get_transaction_type("Fee", "Service or maintenance fee"),
        }

        transactions = {
            "txn_0001": self.get_transaction(
                "TXN-0001",
                transaction_types["deposit"],
                "Cash deposit to Alice checking",
                "COMPLETED",
                self.dt(2026, 1, 10, 9, 15),
            ),
            "txn_0002": self.get_transaction(
                "TXN-0002",
                transaction_types["deposit"],
                "Cash deposit to Bob checking",
                "COMPLETED",
                self.dt(2026, 1, 11, 10, 20),
            ),
            "txn_0003": self.get_transaction(
                "TXN-0003",
                transaction_types["transfer"],
                "Transfer from Alice checking to Carol savings",
                "COMPLETED",
                self.dt(2026, 1, 14, 14, 5),
            ),
            "txn_0004": self.get_transaction(
                "TXN-0004",
                transaction_types["withdrawal"],
                "Cash withdrawal from David checking",
                "COMPLETED",
                self.dt(2026, 1, 18, 16, 45),
            ),
            "txn_0005": self.get_transaction(
                "TXN-0005",
                transaction_types["fee"],
                "Monthly service fee on Alice savings",
                "COMPLETED",
                self.dt(2026, 1, 20, 8, 30),
            ),
            "txn_0006": self.get_transaction(
                "TXN-0006",
                transaction_types["loan_disbursement"],
                "Loan disbursement to Emma savings",
                "COMPLETED",
                self.dt(2026, 1, 25, 11, 0),
            ),
            "txn_0007": self.get_transaction(
                "TXN-0007",
                transaction_types["loan_repayment"],
                "Loan repayment from David salary",
                "COMPLETED",
                self.dt(2026, 2, 2, 9, 40),
            ),
            "txn_0008": self.get_transaction(
                "TXN-0008",
                transaction_types["transfer"],
                "Transfer from Carol savings to Bob checking",
                "COMPLETED",
                self.dt(2026, 2, 7, 13, 10),
            ),
            "txn_0009": self.get_transaction(
                "TXN-0009",
                transaction_types["deposit"],
                "Cash deposit to Frank checking",
                "COMPLETED",
                self.dt(2026, 2, 11, 10, 5),
            ),
            "txn_0010": self.get_transaction(
                "TXN-0010",
                transaction_types["fee"],
                "Overdraft protection fee on Bob checking",
                "COMPLETED",
                self.dt(2026, 2, 14, 15, 25),
            ),
            "txn_0011": self.get_transaction(
                "TXN-0011",
                transaction_types["loan_repayment"],
                "Second loan repayment from David salary",
                "COMPLETED",
                self.dt(2026, 2, 20, 9, 0),
            ),
            "txn_0012": self.get_transaction(
                "TXN-0012",
                transaction_types["loan_repayment"],
                "First loan repayment from Emma savings",
                "COMPLETED",
                self.dt(2026, 3, 3, 12, 15),
            ),
            "txn_0013": self.get_transaction(
                "TXN-0013",
                transaction_types["loan_repayment"],
                "Final loan repayment from Emma savings",
                "COMPLETED",
                self.dt(2026, 3, 15, 12, 15),
            ),
        }

        journal_entries = [
            self.get_journal_entry(transactions["txn_0001"], accounts["system"], "DEBIT", Decimal("1500.00")),
            self.get_journal_entry(transactions["txn_0001"], accounts["alice_checking"], "CREDIT", Decimal("1500.00")),
            self.get_journal_entry(transactions["txn_0002"], accounts["system"], "DEBIT", Decimal("2500.00")),
            self.get_journal_entry(transactions["txn_0002"], accounts["bob_checking"], "CREDIT", Decimal("2500.00")),
            self.get_journal_entry(transactions["txn_0003"], accounts["alice_checking"], "DEBIT", Decimal("400.00")),
            self.get_journal_entry(transactions["txn_0003"], accounts["carol_savings"], "CREDIT", Decimal("400.00")),
            self.get_journal_entry(transactions["txn_0004"], accounts["david_checking"], "DEBIT", Decimal("300.00")),
            self.get_journal_entry(transactions["txn_0004"], accounts["system"], "CREDIT", Decimal("300.00")),
            self.get_journal_entry(transactions["txn_0005"], accounts["alice_savings"], "DEBIT", Decimal("25.00")),
            self.get_journal_entry(transactions["txn_0005"], accounts["system"], "CREDIT", Decimal("25.00")),
            self.get_journal_entry(transactions["txn_0006"], accounts["system"], "DEBIT", Decimal("8000.00")),
            self.get_journal_entry(transactions["txn_0006"], accounts["emma_savings"], "CREDIT", Decimal("8000.00")),
            self.get_journal_entry(transactions["txn_0007"], accounts["david_salary"], "DEBIT", Decimal("800.00")),
            self.get_journal_entry(transactions["txn_0007"], accounts["system"], "CREDIT", Decimal("800.00")),
            self.get_journal_entry(transactions["txn_0008"], accounts["carol_savings"], "DEBIT", Decimal("700.00")),
            self.get_journal_entry(transactions["txn_0008"], accounts["bob_checking"], "CREDIT", Decimal("700.00")),
            self.get_journal_entry(transactions["txn_0009"], accounts["system"], "DEBIT", Decimal("1200.00")),
            self.get_journal_entry(transactions["txn_0009"], accounts["frank_checking"], "CREDIT", Decimal("1200.00")),
            self.get_journal_entry(transactions["txn_0010"], accounts["bob_checking"], "DEBIT", Decimal("15.00")),
            self.get_journal_entry(transactions["txn_0010"], accounts["system"], "CREDIT", Decimal("15.00")),
            self.get_journal_entry(transactions["txn_0011"], accounts["david_salary"], "DEBIT", Decimal("1020.00")),
            self.get_journal_entry(transactions["txn_0011"], accounts["system"], "CREDIT", Decimal("1020.00")),
            self.get_journal_entry(transactions["txn_0012"], accounts["emma_savings"], "DEBIT", Decimal("4300.00")),
            self.get_journal_entry(transactions["txn_0012"], accounts["system"], "CREDIT", Decimal("4300.00")),
            self.get_journal_entry(transactions["txn_0013"], accounts["emma_savings"], "DEBIT", Decimal("4220.00")),
            self.get_journal_entry(transactions["txn_0013"], accounts["system"], "CREDIT", Decimal("4220.00")),
        ]

        loans = {
            "david": self.get_loan(
                customers["david.lee"],
                employees["manager1"],
                Decimal("5000.00"),
                Decimal("13.50"),
                24,
                "ACTIVE",
                self.dt(2026, 1, 5, 10, 0),
                self.dt(2026, 1, 6, 10, 0),
            ),
            "carol": self.get_loan(
                customers["carol.garcia"],
                employees["manager1"],
                Decimal("12000.00"),
                Decimal("11.75"),
                36,
                "APPROVED",
                self.dt(2026, 2, 1, 10, 0),
                self.dt(2026, 2, 3, 10, 0),
            ),
            "emma": self.get_loan(
                customers["emma.davis"],
                employees["manager1"],
                Decimal("8000.00"),
                Decimal("12.25"),
                18,
                "PAID",
                self.dt(2025, 12, 15, 10, 0),
                self.dt(2025, 12, 18, 10, 0),
            ),
        }

        loan_payments = [
            self.get_loan_payment(loans["david"], transactions["txn_0007"], Decimal("800.00"), Decimal("0.00"), self.dt(2026, 2, 2, 9, 45)),
            self.get_loan_payment(loans["david"], transactions["txn_0011"], Decimal("1020.00"), Decimal("0.00"), self.dt(2026, 2, 20, 9, 5)),
            self.get_loan_payment(loans["emma"], transactions["txn_0012"], Decimal("4000.00"), Decimal("300.00"), self.dt(2026, 3, 3, 12, 20)),
            self.get_loan_payment(loans["emma"], transactions["txn_0013"], Decimal("4000.00"), Decimal("220.00"), self.dt(2026, 3, 15, 12, 20)),
        ]

        notifications = [
            self.get_notification(
                customers["alice.johnson"],
                "Salary credited",
                "Your salary account received a credit of 1,500.00.",
                False,
                self.dt(2026, 1, 10, 9, 20),
            ),
            self.get_notification(
                customers["alice.johnson"],
                "Card ending 0001 expiring soon",
                "Your debit card ending 0001 expires in 90 days.",
                True,
                self.dt(2026, 1, 21, 12, 0),
            ),
            self.get_notification(
                customers["bob.smith"],
                "Service fee charged",
                "A service fee of 15.00 has been applied to your account.",
                False,
                self.dt(2026, 2, 14, 15, 30),
            ),
            self.get_notification(
                customers["carol.garcia"],
                "Transfer received",
                "You received 400.00 from Alice Johnson.",
                False,
                self.dt(2026, 1, 14, 14, 10),
            ),
            self.get_notification(
                customers["david.lee"],
                "Loan payment posted",
                "Your loan repayment of 800.00 was posted successfully.",
                True,
                self.dt(2026, 2, 2, 9, 50),
            ),
            self.get_notification(
                customers["emma.davis"],
                "Loan fully repaid",
                "Congratulations, your loan has been fully repaid.",
                False,
                self.dt(2026, 3, 15, 12, 30),
            ),
            self.get_notification(
                customers["frank.moore"],
                "Deposit received",
                "Your checking account was credited with 1,200.00.",
                False,
                self.dt(2026, 2, 11, 10, 10),
            ),
        ]

        audit_logs = [
            self.get_audit_log(admin, "CREATE", "users", admin.id, "Created the administrator account", "127.0.0.1", self.dt(2026, 1, 1, 8, 0)),
            self.get_audit_log(manager, "LOGIN", "users", manager.id, "Manager logged in to review loan applications", "127.0.0.1", self.dt(2026, 1, 5, 9, 30)),
            self.get_audit_log(teller, "CREATE", "transactions", transactions["txn_0001"].id, "Recorded the first cash deposit", "127.0.0.1", self.dt(2026, 1, 10, 9, 20)),
            self.get_audit_log(auditor, "UPDATE", "loans", loans["david"].id, "Reviewed repayment allocation for David Lee", "127.0.0.1", self.dt(2026, 2, 20, 9, 10)),
            self.get_audit_log(manager, "UPDATE", "loans", loans["emma"].id, "Marked Emma Davis loan as paid", "127.0.0.1", self.dt(2026, 3, 15, 12, 35)),
            self.get_audit_log(system_user, "LOGIN", "users", system_user.id, "System user authenticated for batch processing", "127.0.0.1", self.dt(2026, 2, 1, 0, 0)),
        ]

        return {
            "roles": roles,
            "branches": branches,
            "account_types": account_types,
            "customers": customers,
            "employees": employees,
            "accounts": accounts,
            "cards": cards,
            "beneficiaries": beneficiaries,
            "transaction_types": transaction_types,
            "transactions": transactions,
            "journal_entries": journal_entries,
            "loans": loans,
            "loan_payments": loan_payments,
            "notifications": notifications,
            "audit_logs": audit_logs,
        }

    def get_role(self, name):
        role, _ = Role.objects.get_or_create(name=name)
        return role

    def get_branch(self, code, name, address, city):
        branch, _ = Branch.objects.update_or_create(
            branch_code=code,
            defaults={
                "branch_name": name,
                "address": address,
                "city": city,
            },
        )
        return branch

    def get_account_type(self, name, interest_rate, description):
        account_type, _ = AccountType.objects.update_or_create(
            name=name,
            defaults={
                "interest_rate": interest_rate,
                "description": description,
            },
        )
        return account_type

    def get_user(
        self,
        username,
        password,
        role,
        status,
        first_name,
        last_name,
        email,
        is_staff=False,
        is_superuser=False,
    ):
        user, _ = User.objects.update_or_create(
            username=username,
            defaults={
                "role": role,
                "status": status,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
                "is_active": True,
            },
        )
        user.set_password(password)
        user.save(update_fields=[
            "password",
            "role",
            "status",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_superuser",
            "is_active",
        ])
        return user

    def get_customer(self, user, national_id):
        customer, _ = Customer.objects.update_or_create(
            user=user,
            defaults={"national_id": national_id},
        )
        return customer

    def get_employee(self, user, branch, position):
        employee, _ = Employee.objects.update_or_create(
            user=user,
            defaults={
                "branch": branch,
                "position": position,
            },
        )
        return employee

    def get_account(self, customer, branch, account_type, account_number, ledger_balance, available_balance, status, opened_at, closed_at=None):
        account, _ = Account.objects.update_or_create(
            account_number=account_number,
            defaults={
                "customer": customer,
                "branch": branch,
                "account_type": account_type,
                "ledger_balance": ledger_balance,
                "available_balance": available_balance,
                "status": status,
                "opened_at": opened_at,
                "closed_at": closed_at,
            },
        )
        return account

    def get_card(self, account, card_number, card_type, expiry_date, cvv, status):
        card, _ = Card.objects.update_or_create(
            card_number=card_number,
            defaults={
                "account": account,
                "card_type": card_type,
                "expiry_date": expiry_date,
                "cvv": cvv,
                "status": status,
            },
        )
        return card

    def get_beneficiary(self, customer, beneficiary_name, account_number, bank_name, nickname):
        beneficiary, _ = Beneficiary.objects.update_or_create(
            customer=customer,
            account_number=account_number,
            beneficiary_name=beneficiary_name,
            defaults={
                "bank_name": bank_name,
                "nickname": nickname,
            },
        )
        return beneficiary

    def get_transaction_type(self, name, description):
        transaction_type, _ = TransactionType.objects.update_or_create(
            name=name,
            defaults={"description": description},
        )
        return transaction_type

    def get_transaction(self, reference, transaction_type, description, status, created_at):
        transaction, _ = Transaction.objects.update_or_create(
            reference=reference,
            defaults={
                "transaction_type": transaction_type,
                "description": description,
                "status": status,
                "created_at": created_at,
            },
        )
        return transaction

    def get_journal_entry(self, transaction, account, entry_type, amount):
        journal_entry, _ = JournalEntry.objects.update_or_create(
            transaction=transaction,
            account=account,
            entry_type=entry_type,
            amount=amount,
            defaults={},
        )
        return journal_entry

    def get_loan(self, customer, approved_by, principal, interest_rate, term_months, status, created_at, approved_at):
        loan, _ = Loan.objects.update_or_create(
            customer=customer,
            principal=principal,
            created_at=created_at,
            defaults={
                "approved_by": approved_by,
                "interest_rate": interest_rate,
                "term_months": term_months,
                "status": status,
                "approved_at": approved_at,
            },
        )
        return loan

    def get_loan_payment(self, loan, transaction, amount_principal, amount_interest, payment_date):
        loan_payment, _ = LoanPayment.objects.update_or_create(
            transaction=transaction,
            defaults={
                "loan": loan,
                "amount_principal": amount_principal,
                "amount_interest": amount_interest,
                "payment_date": payment_date,
            },
        )
        return loan_payment

    def get_notification(self, customer, title, message, is_read, created_at):
        notification, _ = Notification.objects.update_or_create(
            customer=customer,
            title=title,
            message=message,
            defaults={
                "is_read": is_read,
                "created_at": created_at,
            },
        )
        return notification

    def get_audit_log(self, user, action, table_name, record_id, description, ip_address, created_at):
        audit_log, _ = AuditLog.objects.update_or_create(
            user=user,
            action=action,
            table_name=table_name,
            record_id=record_id,
            description=description,
            ip_address=ip_address,
            defaults={
                "created_at": created_at,
            },
        )
        return audit_log

    def dt(self, year, month, day, hour, minute):
        return datetime(year, month, day, hour, minute, tzinfo=dt_timezone.utc)

    def dt_date(self, year, month, day):
        return datetime(year, month, day, tzinfo=dt_timezone.utc).date()
