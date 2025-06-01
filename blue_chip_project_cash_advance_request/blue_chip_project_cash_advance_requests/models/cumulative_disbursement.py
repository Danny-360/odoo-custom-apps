from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CumulativeDisbursementLine(models.Model):
    _name = 'cumulative.disbursement'
    _description = 'Cumulative Disbursement Line'
    _order = 'id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string='Date', required=True, tracking=True)
    description = fields.Char(string='Description', tracking=True)
    debit = fields.Float(string='Debit', default=0.0, tracking=True)
    credit = fields.Float(string='Credit', default=0.0, tracking=True)
    balance = fields.Float(string='Balance', compute='_compute_balance', store=True, tracking=True)

    debit_account_id = fields.Many2one('account.account', string='Debit Account', required=True, tracking=True)
    credit_account_id = fields.Many2one('account.account', string='Credit Account', required=True, tracking=True)

    currency_id = fields.Many2one('res.currency', string='Currency')

    journal_entry_id = fields.Many2one('account.move', string='Journal Entry', copy=False, readonly="1", tracking=True)
    journal_id = fields.Many2one('account.journal', string='Journal', tracking=True)


    cash_advance_request_id = fields.Many2one(
        'blue_chip_cash_advance',
        string='Cash Advance Request',
        ondelete='cascade'
    )

    total_implementation_cost = fields.Float(
        string='Total Implementation Cost',
        compute='_compute_total_implementation_cost',
        store=True
    )

    current_request_id = fields.Many2one('current.request', string="Current Request",
        domain="[('cash_advance_request_id', '=', cash_advance_request_id)]"
    )

    # request_ids = fields.Many2many(
    # 'current.request',
    # 'disbursement_current_request_rel',  # This is the relation table name
    # 'disbursement_id',                  # This is the column referencing this model
    # 'request_id',                       # This is the column referencing the current.request model
    # string='Related Current Requests', domain="[('id', 'in', request_ids)]" )

    disbursed = fields.Boolean(string="Disbursed", default=False, tracking=True)

    def action_disburse(self):
        for rec in self:
            if rec.current_request_id:
                rec.current_request_id.disbursement_status = 'disbursed'
            rec.disbursed = True

    def action_reset_disbursement(self):
        for rec in self:
            if rec.current_request_id:
                rec.current_request_id.disbursement_status = 'not_disbursed'
            rec.disbursed = False


    @api.depends('cash_advance_request_id', 'cash_advance_request_id.implementation_cost_line_ids.amount')
    def _compute_total_implementation_cost(self):
        for record in self:
            total = sum(record.cash_advance_request_id.implementation_cost_line_ids.mapped('amount'))
            record.total_implementation_cost = total

    @api.depends('cash_advance_request_id.cumulative_disbursement_line_ids.debit')
    def _compute_balance(self):
        for record in self:
            balance = record.total_implementation_cost or 0.0
            for line in record.cash_advance_request_id.cumulative_disbursement_line_ids:
                balance -= line.debit or 0.0
                line.balance = balance

    @api.model
    def create(self, vals):
        record = super().create(vals)
        # Use parent's analytic account field instead
        if not record.cash_advance_request_id.analytic_account_name:
            analytic = self.env['account.analytic.account'].create({
                'name': record.description or 'Auto Analytic - %s' % record.id,
            })
            record.cash_advance_request_id.analytic_account_name = analytic.id
        record._create_journal_entry()
        return record

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if any(field in vals for field in ['debit', 'credit', 'debit_account_id', 'credit_account_id']):
                record._create_journal_entry()
        return res

    def _create_journal_entry(self):
        for record in self:
            # Skip if no debit or credit
            if not (record.debit or record.credit):
                continue

            if not record.debit_account_id or not record.credit_account_id:
                raise ValidationError("Both debit and credit accounts must be selected.")

            if not record.journal_id:
                raise ValidationError("Please select a journal.")

            # Delete existing journal entry if any
            if record.journal_entry_id:
                record.journal_entry_id.button_draft()
                record.journal_entry_id.unlink()

            move_vals = {
                'date': record.date,
                'ref': record.description or 'Cumulative Disbursement',
                'journal_id': record.journal_id.id,
                'line_ids': []
            }

            # Add debit line only if debit > 0
            if record.debit > 0:
                move_vals['line_ids'].append((0, 0, {
                    'account_id': record.debit_account_id.id,
                    'debit': record.debit,
                    'credit': 0.0,
                    'name': record.description,
                    'analytic_distribution': {record.cash_advance_request_id.analytic_account_name.id: 100.0}
                }))

            # Add credit line only if credit > 0
            if record.credit > 0:
                move_vals['line_ids'].append((0, 0, {
                    'account_id': record.credit_account_id.id,
                    'credit': record.credit,
                    'debit': 0.0,
                    'name': record.description,
                }))

            # Create and post the journal entry
            journal_entry = self.env['account.move'].create(move_vals)
            journal_entry.action_post()

            # Link journal entry to this record
            record.journal_entry_id = journal_entry
    

    @api.onchange('current_request_id')
    def _onchange_current_request_id(self):
        for record in self:
            if record.current_request_id:
                # record.description = record.current_request_id.item
                record.description = record.current_request_id.item.name  # or .description
 
                record.debit = record.current_request_id.requested_amount
                record.currency_id = record.current_request_id.currency_id