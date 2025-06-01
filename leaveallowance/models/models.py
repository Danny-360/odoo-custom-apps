# -*- coding: utf-8 -*-

from odoo import models, fields, api


class leave_allowance(models.Model):
    _name = 'leave.allowance'
    _description = 'Leave Allowance'

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee', string='Employee')
    wage = fields.Float(compute="_get_wage", store=True,string="Monthly Basic")
    salary = fields.Float(compute="_get_salary", store=True,string="Salary")
    allowance = fields.Float(compute="_compute_allowance", store=True,string="Leave Allowance")
    taxable_allowance = fields.Float(compute="_compute_taxable_allowance", store=True,string="Taxable Allowance")
    paye_tax = fields.Float(compute="_calculate_paye_tax", store=True,string="PAYE Tax")
    payable = fields.Float(compute="_calculate_payable", store=True,string="Payable")
    months = fields.Integer(string="Number of Months")
    is_proration = fields.Boolean(string="Prorate")
    year_first_day = fields.Datetime(string="First day in the year")
    exit_date = fields.Datetime(string="Exit Date")
    days_worked = fields.Integer(compute="_compute_days_worked", store=True,string="Days Worked")
    months_worked = fields.Integer(compute="_compute_months_worked", store=True,string="Months Worked")
    total_leave_days = fields.Integer(string="Total Leave Days")
    leave_days_not_earned = fields.Integer(string="Leave days not earned", compute="_compute_leave_days_not_earned", store=True)
    leave_days_earned = fields.Integer(string="Leave days earned",compute="_compute_leave_days_earned", store=True)
    leave_allowance_earned = fields.Float(string="Leave allowance earned",compute="_compute_allowance_earned", store=True)




    @api.depends('employee_id')
    def _get_wage(self):
        # allocations_read = self.env['hr.leave.allocation']
        # allocation_type_name = "Paid Time Off"
        contract_history_model = self.env['hr.contract.history']
        
        for record in self:
            if record.employee_id:
                # Search for the contract related to the employee
                contract_item = contract_history_model.search([('employee_id', '=', record.employee_id.id)], limit=1)
                
                if contract_item:
                    # If a contract is found, assign its wage to record.wage
                    record.wage = contract_item.wage
                else:
                    # If no contract found, set wage to 0 or any default value
                    record.wage = 0.0
            else:
                # If employee_id is None, set wage to 0 or any default value
                record.wage = 0.0

    @api.depends('wage','months')
    def _get_salary(self):
        for record in self:
            record.salary = record.wage * record.months

    @api.depends('wage','months')
    def _compute_allowance(self):
        for record in self:
            record.allowance = record.salary * 0.1

    @api.depends('wage','months','allowance')
    def _compute_taxable_allowance(self):
        for record in self:
            if record.allowance:
                record.taxable_allowance = record.allowance - (((record.allowance * 12)*0.2)+200000)/12
            else:
                record.taxable_allowance = 0


    @api.depends('wage', 'months','taxable_allowance')
    def _calculate_paye_tax(self):
        for record in self:
            annual_income = 0
            tax = 0
            if record.taxable_allowance:
                print(record.allowance,record.taxable_allowance)
                annual_income = record.taxable_allowance * 12 

            # Define tax tiers as tuples of (threshold, rate)
            tax_tiers = [
                (300000, 0.07),
                (300000, 0.11),
                (500000, 0.15),
                (500000, 0.19),
                (1600000, 0.21),
                (float('inf'), 0.24)
            ]
            
            previous_threshold = -1
            print(annual_income > previous_threshold)
            for threshold, rate in tax_tiers:
                if annual_income > previous_threshold:
                    applicable_income = min(annual_income, previous_threshold + threshold) - previous_threshold
                    tax += applicable_income * rate
                previous_threshold += threshold

            # Convert annual tax to monthly tax
            record.paye_tax = tax / 12



    @api.depends('months')
    def _calculate_payable(self):
        for record in self:
            record.payable = record.allowance - record.paye_tax if record.allowance and record.paye_tax else 0

    @api.depends('year_first_day', 'exit_date')
    def _compute_days_worked(self):
        for record in self:
            if record.year_first_day:
                # Use exit_date if it exists, otherwise use the current date
                end_date = record.exit_date or fields.Datetime.now() if record.exit_date else fields.Datetime.now()
                
                # Calculate the difference in days
                delta = end_date - record.year_first_day
                record.days_worked = int(delta.days + delta.seconds / 86400)  # Converts seconds to a fraction of a day
            else:
                # Set days worked to 0 if year_first_day is not set
                record.days_worked = 0

    @api.depends('year_first_day', 'exit_date')
    def _compute_months_worked(self):
        for record in self:
            if record.days_worked:
                record.months_worked = int(record.days_worked / 30)  
            else:
                record.months_worked = int(0.0)

    @api.depends('total_leave_days')
    def _compute_leave_days_earned(self):
        for record in self:
            if record.months_worked:
                record.leave_days_earned = int((record.months_worked * record.total_leave_days)/12)
            else:
                # Set days worked to 0 if year_first_day is not set
                record.leave_days_earned = 0
    
    @api.depends('total_leave_days')
    def _compute_leave_days_not_earned(self):
        for record in self:
            if record.leave_days_earned:
                record.leave_days_not_earned = record.total_leave_days - record.leave_days_earned
            else:
                # Set days worked to 0 if year_first_day is not set
                record.leave_days_not_earned = record.total_leave_days

    @api.depends('is_proration', 'year_first_day', 'exit_date','payable','employee_id','total_leave_days')
    def _compute_allowance_earned(self):
        for record in self:
            l_days = record.total_leave_days if record.total_leave_days else 0
            l_payable = record.payable if record.payable else 0
            l_earned = record.leave_days_earned if record.leave_days_earned else 0
            if record.is_proration:
                # record.send_notification_email()
                # record.leave_allowance_earned = l_earned
                record.leave_allowance_earned = (((l_payable / l_days)) * l_earned) if l_payable else 0
            else:
                record.leave_allowance_earned = l_payable if l_payable else 0
    

    # def create(self, vals):
    #     print(vals)
    #     record = super(leave_allowance, self).create(vals)
        
    #     # Send email after record creation
    #     record.send_notification_email()
        
    #     return record

    def send_notification_email(self):
        template = self.env.ref('leaveallowance.email_template_leave')
        for record in self:
            # Check if the template exists
            if template:
                template.send_mail(record.id, force_send=True)