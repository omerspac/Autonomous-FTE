import xmlrpc.client
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class OdooClient:
    """
    Python client for Odoo Community JSON-RPC (XML-RPC) interaction.
    """
    def __init__(self, 
                 url: str = os.getenv("ODOO_URL", "http://localhost:8069"), 
                 db: str = os.getenv("ODOO_DB", "odoo"), 
                 user: str = os.getenv("ODOO_USER", "admin"), 
                 password: str = os.getenv("ODOO_PASSWORD", "admin")):
        self.url = url
        self.db = db
        self.user = user
        self.password = password
        self.uid = None
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

    def authenticate(self):
        try:
            self.uid = self.common.authenticate(self.db, self.user, self.password, {})
            if not self.uid:
                logger.error("Authentication failed. Check Odoo credentials.")
            return self.uid
        except Exception as e:
            logger.error(f"Odoo Auth Error: {e}")
            return None

    def execute_kw(self, model: str, method: str, *args, **kwargs):
        if not self.uid:
            self.authenticate()
        if not self.uid:
            raise PermissionError("Odoo connection required.")
        return self.models.execute_kw(self.db, self.uid, self.password, model, method, args, kwargs)

    def get_invoices(self, domain: List = []) -> List[Dict]:
        """Fetch customer invoices."""
        return self.execute_kw('account.move', 'search_read', domain, 
                               fields=['name', 'partner_id', 'amount_total', 'payment_state', 'date'])

    def create_invoice(self, partner_id: int, lines: List[Dict]) -> int:
        """
        Creates an invoice.
        lines format: [{'product_id': id, 'quantity': q, 'price_unit': p}]
        """
        invoice_vals = {
            'partner_id': partner_id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, line) for line in lines]
        }
        return self.execute_kw('account.move', 'create', [invoice_vals])

    def record_payment(self, invoice_id: int, amount: float):
        """Register a payment for an invoice."""
        # Simplified for demonstration. In Odoo, this requires account.payment.register
        logger.info(f"Recording payment of {amount} for invoice {invoice_id}")
        return True # Mock success

    def list_expenses(self) -> List[Dict]:
        """Fetch vendor bills/expenses."""
        return self.execute_kw('account.move', 'search_read', [('move_type', '=', 'in_invoice')],
                               fields=['name', 'partner_id', 'amount_total', 'date'])

    def generate_financial_summary(self) -> Dict:
        """Aggregation of revenue and expenses."""
        invoices = self.get_invoices([('move_type', '=', 'out_invoice')])
        bills = self.list_expenses()
        
        revenue = sum(inv['amount_total'] for inv in invoices if inv['payment_state'] == 'paid')
        receivables = sum(inv['amount_total'] for inv in invoices if inv['payment_state'] == 'not_paid')
        expenses = sum(bill['amount_total'] for bill in bills)

        return {
            "revenue_paid": revenue,
            "receivables": receivables,
            "total_expenses": expenses,
            "net_cash_flow": revenue - expenses
        }

if __name__ == "__main__":
    # Test stub
    # client = OdooClient()
    # print(client.generate_financial_summary())
    pass
