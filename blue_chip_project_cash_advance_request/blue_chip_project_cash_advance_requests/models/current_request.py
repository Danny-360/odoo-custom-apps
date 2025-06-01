from odoo import models, fields, api

class CurrentRequest(models.Model):
    _name = 'current.request'
    _description = 'Current Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name='item'
    description = fields.Char(string='Item', tracking=True)
    requested_amount = fields.Float(string='Requested Amount', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', tracking=True)
    item = fields.Many2one('implementation.cost', string='Description', domain="[('cash_advance_request_id', '=', cash_advance_request_id)]", tracking=True)
    # item = fields.Text(string='Items')
    cash_advance_request_id = fields.Many2one('blue_chip_cash_advance', string='Cash Advance Request', required=True, tracking=True)
    implementation_cost_line_ids = fields.Many2one('implementation.cost', string='Implementation Cost', tracking=True)
    cumulative_disbursement_created = fields.Boolean(string='Disbursement Created', default=False, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ], string='State', default='draft', tracking=True)


    approval_status = fields.Selection([
        ('not_approved', 'Not Approved'),
        ('approved', 'Approved'),
    ], string='Approval Status', default='not_approved', readonly=True, tracking=True)

    disbursement_status = fields.Selection([
        ('not_disbursed', 'Not Disbursed'),
        ('disbursed', 'Disbursed'),
    ], string='Disbursement Status', default='not_disbursed', readonly=True, tracking=True)


    @api.depends('approval_status', 'disbursement_status', 'state')
    def _compute_editable(self):
        for record in self:
            record.is_editable = record.state in ('draft', 'refused') and \
                                record.approval_status == 'not_approved' and \
                                record.disbursement_status == 'not_disbursed'

    is_editable = fields.Boolean(compute='_compute_editable', store=True)
    approved = fields.Boolean(compute='_compute_approved', store=True, tracking=True)

    # def action_approve_request(self):
    #     for record in self:
    #         record.approval_status = 'approved'

    @api.depends('approval_status')
    def _compute_approved(self):
        for rec in self:
            rec.approved = (rec.approval_status == 'approved')


    def action_approve(self):
        for rec in self:
            if rec.approval_status != 'approved':
                rec.approval_status = 'approved'

    
    def action_reset_to_draft(self):
        for rec in self:
            rec.approval_status = 'not_approved'




    @api.onchange('item')
    def _onchange_item(self):
        if self.item:
            self.requested_amount = self.item.amount
            self.currency_id = self.item.currency_id.id
            self.description = self.item.description
    

    @api.onchange('cash_advance_request_id')
    def _onchange_cash_advance_request_id(self):
        if self.cash_advance_request_id:
            return {
                'domain': {
                    'item': [('cash_advance_request_id', '=', self.cash_advance_request_id.id)]
                }
            }
        return {'domain': {'item': []}}
    

    def name_get(self):
        result = []
        for record in self:
            name = record.item.name or record.item.description or 'Unnamed Request'
            result.append((record.id, name))
        return result
