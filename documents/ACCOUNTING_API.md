# Accounting System API Documentation

## Odoo Infrastructure
- **Base Image**: Odoo Community 17.0
- **Database**: PostgreSQL 15
- **Communication Protocol**: XML-RPC (Odoo Standard)

## Python Client (odoo_client.py)
A wrapper for Odoo models.

### Methods:
- `get_invoices(domain=[])`: Fetch customer invoices (account.move).
- `create_invoice(partner_id, lines)`: Create a draft invoice.
- `record_payment(invoice_id, amount)`: Register a payment.
- `list_expenses()`: Fetch vendor bills.
- `generate_financial_summary()`: Aggregate P&L data.

## MCP Server (accounting-mcp)
Exposes accounting tools to the AI Orchestrator.

### Tools:
1. **`create_invoice`**
   - Args: `partner_id`, `amount`, `description`
2. **`record_payment`**
   - Args: `invoice_id`, `amount`
3. **`get_financial_report`**
   - Returns a summary of revenue, receivables, and expenses.
4. **`list_overdue_invoices`**
   - Returns a list of unpaid customer invoices.

## Security
- **Authentication**: Odoo UID + Password (via environment variables).
- **Dry Run**: Set `DRY_RUN=true` to simulate Odoo actions without affecting the database.
- **Auditing**: Every call is logged by the Orchestrator's action layer.
