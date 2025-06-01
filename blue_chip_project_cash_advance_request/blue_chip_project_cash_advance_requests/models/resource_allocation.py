# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResourceAllocation(models.Model):
    _inherit = 'blue_chip_cash_advance'
 

    resource_name = fields.Char(string='Resource Name', tracking=True)
    request_date = fields.Date(string='Request Date', tracking=True)
    project_account_code = fields.Char(string='Project Account Code')
    project_location = fields.Char(string='Project Location', tracking=True)
    site_id = fields.Char(string = 'Site ID', tracking=True)
    implementation_cost = fields.Float(string = 'Implementation Cost')
    team_lead = fields.Many2one('hr.employee', string='Team Lead', tracking=True)
    freelance = fields.Integer(string = 'Freelance Needed', tracking=True)
    riggers = fields.Integer(string = 'Riggers', tracking=True)
    engineer = fields.Integer(string = 'Engineer', tracking=True)
    ehs_vehicle = fields.Integer(string = 'EHS Vehicle', tracking=True)
    canter_truck = fields.Integer(string = 'Canter Truck', tracking=True)
    cash_advance_request_id = fields.Many2one('blue_chip_cash_advance', string='Cash Advance Request', ondelete='cascade', tracking=True)


    @api.onchange('project_account_code')
    def _onchange_project_account_code(self):
        if not self.project_account_code or not hasattr(self.project_account_code, 'id'):
            self.project_account_code = False