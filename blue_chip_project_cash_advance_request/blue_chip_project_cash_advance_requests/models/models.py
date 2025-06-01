# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)



class cash_advance_request(models.Model):
    _name = 'blue_chip_cash_advance'
    _description = 'Project Cash Advance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Project Name", tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', tracking=True)
    analytic_account_name = fields.Many2one('account.analytic.account', string='Analytic Account',
        store=True, ondelete='cascade', 
        help='Analytic Account linked to this cash advance request.', tracking=True)

    project_manager_id = fields.Many2one('hr.employee', string='Project Manager', tracking=True)
    project_description = fields.Text(string='Project Description', tracking=True)
    project_duration = fields.Integer(string='Project Duration', tracking=True)
    is_active = fields.Boolean(string='Is Active', default=True, tracking=True)
    caf_no = fields.Char(string='CAF No', tracking=True)
    implementation_cost_line_ids = fields.One2many('implementation.cost', 'cash_advance_request_id', string='Implementation Cost', tracking=True)

    total_implementation_cost = fields.Float(
        string='Total',
        compute='_compute_total_implementation_cost',
        store=True, 
    )

    implementation_budget_line_ids = fields.One2many(
        'implementation.budget',
        'cash_advance_request_id',
        string='Implementation Budget'
    )

    # cumulative disbursement field
    cumulative_disbursement_line_ids = fields.One2many(
        'cumulative.disbursement',
        'cash_advance_request_id',
        string='Cumulative Disbursement'
    )

    # current requests
    current_request_id = fields.One2many(
        'current.request',
        'cash_advance_request_id',
        string='Current Request'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('chro', 'CHRO'),
        ('pm', 'PM'),
        ('cmo', 'CMO'),
        ('cto', 'CTO'),
        ('md', 'MD/CEO'),
        ('cfo', 'CFO'),
    ], string='Approval State', default='draft', tracking=True)

    

    # # Automatically create an analytic account    
    @api.model
    def create(self, vals):
        if not vals.get('analytic_account_name'):
            analytic_account = self.env['account.analytic.account'].create({
                'name': vals.get('name', 'Unnamed Project'),
                'company_id': self.env.company.id,
                # Set a default plan_id value (You can replace 1 with your actual plan ID)
                'plan_id': self.env['account.analytic.plan'].search([], limit=1).id,  # Ensure this points to the correct plan model
            })
            vals['analytic_account_name'] = analytic_account.id

        return super(cash_advance_request, self).create(vals)
    


    
    # computation for auto-populating the implementation budget
    @api.depends('implementation_cost_line_ids.amount')
    def _compute_total_implementation_cost(self):
        for record in self:
            record.total_implementation_cost = sum(
                line.amount for line in record.implementation_cost_line_ids
            )

    # Auto populating the implementation budget data from the sales order
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        if self.sale_order_id:
            # Clear existing lines
            self.implementation_budget_line_ids = [(5, 0, 0)]
            # Auto-create line
            line_data = {
                'description': self.sale_order_id.note or "No description provided.",
                'sale_order_id': self.sale_order_id.id,
                'sale_order_amount': self.sale_order_id.amount_total,
                'currency_id': self.sale_order_id.currency_id.id
            }
            self.implementation_budget_line_ids = [(0, 0, line_data)]
        

    # Action to auto-populate and create the current request
    def action_md_approve(self):
        _logger.info("MD/CEO approval triggered")
        self.state = 'md'
        # for req in self.current_request_id.filtered(lambda r: r.state != 'approved'):
        #     req.state = 'approved'
        #     self._generate_cumulative_disbursements()

    def action_cfo_approve(self):
        self.state = 'cfo'

    def action_cto_approve(self):
        self.state = 'cto'

    def action_pm_approve(self):
        self.state = 'pm'

    def action_cmo_approve(self):
        self.state = 'cmo'

    def action_chro_approve(self):
        self.state = 'chro'


    # action for refuse button
    def action_refuse(self):
        for record in self:
            record.state = 'draft'

    
    # To autopopulate the Cumulative disbursement model
    def _generate_cumulative_disbursements(self):
        requests = self.current_request_id.filtered(lambda r: r.state == 'approved' and not r.cumulative_disbursement_created)
        if not requests:
            raise UserError("No approved current requests to generate disbursements.")
        # default_debit_account = self.env['account.account'].search([('user_type_id.type', '=', 'receivable')], limit=1)
        # default_credit_account = self.env['account.account'].search([('user_type_id.type', '=', 'payable')], limit=1)
        default_debit_account = self.env['account.account'].search([('account_type', '=', 'asset_receivable')], limit=1)
        default_credit_account = self.env['account.account'].search([('account_type', '=', 'liability_payable')], limit=1)
 
        if not default_debit_account or not default_credit_account:
            raise UserError("Default debit or credit accounts could not be found. Please configure chart of accounts.")
        for request in requests:
            vals = {
                'cash_advance_request_id': self.id,
                'description': f"{request.item.name if request.item else ''} - {request.description or ''}".strip(' -'),
                'debit': request.requested_amount,
                'credit': 0.0,
                'date': fields.Date.today(),
                'debit_account_id': default_debit_account.id,
                'credit_account_id': default_credit_account.id,
                }
            self.env['cumulative.disbursement'].create(vals)
            request.cumulative_disbursement_created = True

    