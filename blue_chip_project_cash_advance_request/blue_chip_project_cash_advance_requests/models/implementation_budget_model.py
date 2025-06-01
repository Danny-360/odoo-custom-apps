# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ImplementationBudget(models.Model):
    _name = 'implementation.budget'
    _description = 'Implementation Budget'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    cash_advance_request_id = fields.Many2one('blue_chip_cash_advance', string='Cash Advance Request')
    # amount = fields.Float(string='Amount')
    # sequence = fields.Integer(string='Sequence', default=10)
    # currency_id = fields.Many2one('res.currency', string='Currency')
    # date = fields.Date(string='Date')
    description = fields.Text(string='Description', tracking=True)

    sale_order_id = fields.Many2one('sale.order', string="PO Value", related="cash_advance_request_id.sale_order_id", store=True, readonly=True, tracking=True)
    sale_order_amount = fields.Monetary(string="Total Amount", currency_field='currency_id', compute="_compute_sale_order_details", store=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency", related="sale_order_id.currency_id", store=True, readonly=True, tracking=True)


    @api.depends('sale_order_id')
    def _compute_sale_order_details(self):
        for record in self:
            if record.sale_order_id:
                record.sale_order_amount = record.sale_order_id.amount_total
                # record.sale_order_description = record.sale_order_id.note or "No description provided."
            else:
                record.sale_order_amount = 0.0
                # record.sale_order_description = ""
