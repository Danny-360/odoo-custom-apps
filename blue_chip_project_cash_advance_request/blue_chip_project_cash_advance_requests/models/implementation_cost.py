
from odoo import models, fields, api


class ImplementationCost(models.Model):
    _name = 'implementation.cost'
    _description = 'Implementation Cost'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Description', required=True, tracking=True)
    cash_advance_request_id = fields.Many2one('blue_chip_cash_advance', string='Cash Advance Request', tracking=True)
    amount = fields.Float(string='Amount', tracking=True)
    sequence = fields.Integer(string='Sequence', default=10, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', tracking=True)
    # date = fields.Date(string='Date')
    description = fields.Text(string='Description', tracking=True)

    current_request_id = fields.One2many('current.request', 'implementation_cost_line_ids', string='Current Requests')
    

