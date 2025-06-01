# -*- coding: utf-8 -*-  

import json
import logging
from odoo import models, fields, api
from urllib.parse import quote, urlencode
from odoo.exceptions import AccessError
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class ProjectEnhancement(models.Model):
    _inherit = 'project.project'

    # Fields definitions
    pmo = fields.Many2one(
        'hr.employee',
        string='PMO',
        default=lambda self: self._get_pmo(),
    )

    project_manager = fields.Many2one(
        'hr.employee',
        string='Project Manager',
        domain="[('department_id', '=', 3)]"
    )

    starting_date = fields.Date(
        string="Starting Date", 
        # help="Project start date"
        )
    ending_date = fields.Date(
        string="Ending Date", 
        # help="Project end date"
        )    
    department_id = fields.Many2one(
        'hr.department', string='Department',
        help='Select the department associated with this project'
    )
    department_manager_id = fields.Many2one(
        'hr.employee', string='Department Manager',
        domain="[('department_id', '=', department_id)]",
        help='Manager of the selected department',
        readonly=True,  # Keep it readonly
        store=True,
        compute="_compute_department_manager"
    )
    team_lead_id = fields.Many2one(
        'hr.employee', string='Team Lead',
        domain="[('department_id', '=', department_id)]",
        store=True,
        help='Employee responsible for leading the team in the selected department for this project'
    )
    status = fields.Selection(
        [('active', 'Active'),
         ('on_hold', 'On Hold'),
         ('deprioritized', 'De-prioritized'),
         ('closed', 'Closed')],
        string='Status',
        default='active',
        required=True
    )
    expense_ids = fields.One2many('hr.expense', 'project_id', readonly=True, store=True)
    #timesheet_ids = fields.One2many('account.analytic.line', 'project_id', string="Timesheets", readonly=True)  # Make it readonly
    budget = fields.Monetary(string='Total Budget', currency_field='currency_id')
    budget_utilized = fields.Monetary(string='Budget Utilized', compute='_compute_budget_utilized', store=True)
    budget_remaining = fields.Monetary(string='Remaining Budget', compute='_compute_budget_remaining', store=True)
    profitability = fields.Monetary(string='Profitability', compute='_compute_profitability', store=True)
    forecasted_budget_overrun = fields.Monetary(string='Forecasted Budget Overrun', compute='_compute_forecasted_overrun', store=True)
    budget_alert_threshold = fields.Float(string="Budget Alert Threshold (%)", default=80.0)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', store=True)
    currency_symbol = fields.Char(related='currency_id.symbol', string="Currency Symbol")
    task_ids = fields.One2many('project.task', 'project_id', string='Tasks')
    task_names = fields.Char(string="Task Names", compute="_compute_task_names", store=True)

   # timesheet_cost = fields.Monetary(string='Timesheet Cost', currency_field='currency_id', compute='_compute_timesheet_cost', store=True)

    # New Field to Track If Alert Was Sent
    budget_alert_sent = fields.Boolean(string='Budget Alert Sent', default=False)
    
        # Add fields to track if roles have been accepted or declined
    role_accepted = fields.Boolean(string="Role Accepted", default=False)
    role_declined = fields.Boolean(string="Role Declined", default=False)
    
    
    def _get_pmo(self):
        """Fetch the manager of the department with id = 3, using sudo to bypass access control."""
        department = self.env['hr.department'].sudo().browse(3)  # Use sudo to bypass access control
        if department and department.manager_id:
            return department.manager_id.id
        return False  # In case no manager is found


# For start and end date: to ensure the end date comes after the start date
    @api.constrains('starting_date', 'ending_date')
    def _check_dates(self):
        for record in self:
            if record.starting_date and record.ending_date and record.starting_date > record.ending_date:
                raise ValidationError("End Date must be after Start Date.")
            

# Departmental manager should only be able to edit the Team Lead field
    @api.model
    def write(self, vals):
        messages = []  # Store notifications
        
        # Check if the user is a Departmental Manager
        if self.env.user.has_group('project_enhancement.group_project_department_manager'):
            restricted_fields = set(vals.keys()) - {'team_lead_id'}
            if restricted_fields:
                raise AccessError("You are only allowed to modify the Team Lead field.")

        for record in self:
            if 'department_id' in vals and record.department_id.id != vals['department_id']:
                new_department = self.env['hr.department'].browse(vals['department_id']).name
                messages.append(f"Department changed to {new_department}")

            if 'department_manager_id' in vals and record.department_manager_id.id != vals['department_manager_id']:
                new_manager = self.env['hr.employee'].browse(vals['department_manager_id']).name
                messages.append(f"Department Manager changed to {new_manager}")

            if 'team_lead_id' in vals and record.team_lead_id.id != vals['team_lead_id']:
                new_team_lead = self.env['hr.employee'].browse(vals['team_lead_id']).name
                messages.append(f"Team Lead changed to {new_team_lead}")

            if 'project_manager' in vals and record.project_manager.id != vals['project_manager']:
                new_pm = self.env['hr.employee'].browse(vals['project_manager']).name
                messages.append(f"Project Manager changed to {new_pm}")

        # Send real-time notification inside Odoo
        if messages:
            self._send_odoo_notification("<br/>".join(messages))

        return super(ProjectEnhancement, self).write(vals)

    def _send_odoo_notification(self, message):
        """Send in-app notification inside Odoo."""
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Project Update',
                'message': message,
                'type': 'info',  # Can be 'success', 'warning', 'danger'
                'sticky': False,  # True to keep it on screen
            }
        }
        return self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', notification)



    @api.depends('department_id')
    def _compute_department_manager(self):
        """Update the Department Manager and clear Team Lead when the department changes.""" 
        if self.department_id:
            self.department_manager_id = self.department_id.manager_id
            self.team_lead_id = False
            # Send email to department manager when department is assigned
            if self.department_manager_id:
                self._send_role_assignment_email(self, 'department_manager')
                self.message_notify(body=f"Department Manager set to {self.department_manager_id.name}")

        else:
            self.department_manager_id = False
            self.team_lead_id = False

    @api.depends('task_ids.name')
    def _compute_task_names(self):
        for project in self:
            project.task_names = ', '.join(project.task_ids.mapped('name'))
            
            
            
    # base generating base url       
    def _get_base_url(self):
        """Retrieve the base URL from Odoo's configuration dynamically."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return base_url.rstrip('/')



    # @api.depends('timesheet_ids.unit_amount', 'timesheet_ids.employee_id')
    # def _compute_timesheet_cost(self):
    #     """Compute the cost of the timesheets associated with the project.""" 
    #     for project in self:
    #         total_cost = 0.0
    #         for timesheet in project.timesheet_ids:
    #             hourly_rate = timesheet.employee_id.hourly_cost or 0.0  # Assuming hourly_rate field exists in hr.employee
    #             total_cost += timesheet.unit_amount * hourly_rate
    #         project.timesheet_cost = total_cost

    @api.depends('expense_ids',) # 'timesheet_cost')
    def _compute_budget_utilized(self):
        """Compute the total utilized budget including expenses and timesheet costs.""" 
        for project in self:
            total_expenses = sum(expense.total_amount for expense in project.expense_ids)
            project.budget_utilized = total_expenses #+ project.timesheet_cost
            # Check the budget alert whenever the utilized budget changes
            project._check_budget_alert()

    def _send_role_assignment_email(self, project, role):
        """Send role assignment email to the assigned role."""
        employee = None
        subject = ''
        body_html = ''

        # Ensure the role is passed correctly and check if the role corresponds to the project role.
        if role == 'project_manager' and project.project_manager:
            employee = project.project_manager
            subject = f"You have been assigned as Project Manager for the project: {project.name}"
            body_html = f"<p>Dear {employee.name},</p><p>You have been assigned as <b>Project Manager</b> for the project: {project.name}.</p>"
        elif role == 'team_lead' and project.team_lead_id:
            employee = project.team_lead_id
            subject = f"You have been assigned as Team Lead for the project: {project.name}"
            body_html = f"<p>Dear {employee.name},</p><p>You have been assigned as <b>Team Lead</b> for the project: {project.name}.</p>"
        elif role == 'department_manager' and project.department_manager_id:
            employee = project.department_manager_id
            subject = f"You have been assigned as Department Manager for the project: {project.name}"
            body_html = f"<p>Dear {employee.name},</p><p>You have been assigned as <b>Department Manager</b> for the project: {project.name}.</p>"

        if employee and employee.work_email:
            # Get the base URL to generate the full link
            base_url = self._get_base_url()  # Retrieve the base URL dynamically
            
            # Assign the parameters as variables
            project_name = project.name
            assigned_by = project.write_uid  # Get the ID of the user assigning the role
            role_assigned = role

            # Construct the context dictionary
            context_dict = {
                'project_name': project_name,
                'role': role_assigned,
                'assigned_by': assigned_by.id
            }

            # URL-encode the context dictionary correctly (use JSON stringify)
            encoded_context = quote(json.dumps(context_dict))  # Safe encoding

            # Create the full URL to be sent to the recipient (passing assigned_by.id)
            action_url = f"{base_url}/web#action=project_enhancement.action_role_assignment_wizard&model=role.assignment.wizard&view_type=form&context={encoded_context}"

            # Adding the link in the email body and who assigned the role
            body_html += f"<p>This role has been assigned to you by {assigned_by.name}. You can accept or decline this role using the following link: <a href='{action_url}'>Accept/Decline Role</a></p>"

            # Creating the email values
            email_values = {
                'subject': subject,
                'body_html': body_html,
                'email_to': employee.work_email,
            }

            # Create and send the email
            mail = self.env['mail.mail'].create(email_values)
            mail.send()

    def _send_project_creation_email(self, project):
        """Send an email when a project is created to the PMO (Department Manager)."""
        user_name = project.create_uid.name  # The creator of the project

        # Get the base URL to generate the full project link
        base_url = self._get_base_url()  # Retrieve the base URL dynamically
        
        # Create the link to the project in the email (using the project ID to generate a URL)
        project_link = f"{base_url}/web#id={project.id}&model=project.project&view_type=form"

        # Prepare the email content with the project link
        email_values = {
            'subject': f"New Project Onboarded: {project.name}",
            'body_html': f"<p>Dear {project.pmo.name},</p><p>A new project has been onboarded: <b>{project.name}</b>.</p>"
                        f"<p>The project was created by {user_name}. This project requires your attention.</p>"
                        f"<p>You can view and manage the project by following this link: <a href='{project_link}'>View Project</a></p>",
            'email_to': project.pmo.work_email,  # Send to the PMO (Department Manager)
        }

        # Create and send the email
        mail = self.env['mail.mail'].create(email_values)
        mail.send()




    @api.depends('budget', 'budget_utilized')
    def _compute_budget_remaining(self):
        """Compute the remaining budget.""" 
        for project in self:
            project.budget_remaining = project.budget - project.budget_utilized

    @api.depends('budget', 'budget_utilized')
    def _compute_profitability(self):
        """Compute the profitability as the difference between the budget and utilized budget.""" 
        for project in self:
            project.profitability = project.budget - project.budget_utilized

    @api.depends('budget_utilized')
    def _compute_forecasted_overrun(self):
        """Compute forecasted overrun based on current budget utilization trends.""" 
        for project in self:
            if project.budget_utilized > project.budget:
                project.forecasted_budget_overrun = project.budget_utilized - project.budget
            else:
                project.forecasted_budget_overrun = 0.0

    def _check_budget_alert(self):
        """Check if the project has exceeded the configured budget alert threshold.""" 
        for project in self:
            if project.budget and project.budget_utilized / project.budget * 100 >= project.budget_alert_threshold and not project.budget_alert_sent:
                self._send_budget_alert(project)
                
                

    def _send_budget_alert(self, project):
        """Send an alert email to the PMO if the project budget threshold is exceeded."""
        if project.pmo and project.pmo.work_email:
            # Get the base URL to generate the full project link
            base_url = self._get_base_url()  # Retrieve the base URL dynamically
            
            # Generate the project link using the base URL
            project_link = f"{base_url}/web#id={project.id}&model=project.project&view_type=form"
            
            subject = f"Budget Alert: {project.name} has exceeded the threshold"
            body_html = f"<p>Dear {project.pmo.name},</p><p>The project {project.name} has exceeded the configured budget alert threshold of {project.budget_alert_threshold}%.</p>" \
                        f"<p>You can view the project details here: <a href='{project_link}'>View Project</a></p>"

            email_values = {
                'subject': subject,
                'body_html': body_html,
                'email_to': project.pmo.work_email,
            }

            # Create and send the email
            mail = self.env['mail.mail'].create(email_values)
            mail.send()

            # Set the flag to prevent further alerts until budget changes
            project.budget_alert_sent = True




    # Override create method to pre-populate the PMO and send notifications.
    @api.model
    def create(self, vals):
        
        # Ensure the 'pmo' field is populated
        if 'pmo' not in vals:
            vals['pmo'] = self._get_pmo()

        project = super(ProjectEnhancement, self).create(vals)

        # Send email to PMO (department manager)
        if project.pmo:
            self._send_project_creation_email(project)

        # Send email to the project manager (if assigned)
        if project.project_manager:
            self._send_role_assignment_email(project, 'project_manager')

        # Check for budget alert if applicable
        project._check_budget_alert()

        return project


    def write(self, vals):
        """Override write method to send notifications when updating a project.""" 
        for project in self:
            # Log role changes in the chatter (e.g., Project Manager or Department Manager assignment)
            if 'project_manager' in vals:
                project_manager = self.env['hr.employee'].browse(vals['project_manager'])
                project.message_post(body=f"Project Manager set to {project_manager.name}", message_type="notification", subtype_xmlid="mail.mt_comment")

            if 'department_manager_id' in vals:
                department_manager = self.env['hr.employee'].browse(vals['department_manager_id'])
                project.message_post(body=f"Department Manager set to {department_manager.name}", message_type="notification", subtype_xmlid="mail.mt_comment")

            if 'team_lead_id' in vals:
                team_lead = self.env['hr.employee'].browse(vals['team_lead_id'])
                project.message_post(body=f"Team Lead set to {team_lead.name}", message_type="notification", subtype_xmlid="mail.mt_comment")

            # Update department manager and team lead if department changes
            if 'department_id' in vals:
                department_id = vals.get('department_id') or project.department_id.id
                department = self.env['hr.department'].browse(department_id)
                vals['department_manager_id'] = department.manager_id.id if department.manager_id else False

            res = super(ProjectEnhancement, self).write(vals)

            # Send role assignment emails for updated roles
            if 'project_manager' in vals:
                project._send_role_assignment_email(project, 'project_manager')
            if 'department_manager_id' in vals:
                project._send_role_assignment_email(project, 'department_manager')
            if 'team_lead_id' in vals:
                project._send_role_assignment_email(project, 'team_lead')

            if 'expense_ids' in vals:
                project._check_budget_alert()

        return res

    
    
    # Role View Restrictions and project counts
    total_project = fields.Integer(string="Total active Projects", compute="_compute_total_project")

    @api.model
    def _compute_total_project(self):
        """Compute the total number of projects the user can see."""
        # Get the current user
        current_user = self.env.user

        # If the user is an admin, they should see all projects
        if current_user.has_group('base.group_system'):
            self.total_project = self.env['project.project'].search_count([])  # Admin can see all projects
        else:
            # Define a domain to filter projects that the user has access to
            domain = [
                '|', '|', '|',  # This represents OR conditions for each field
                ('pmo', '=', current_user.employee_id.id),  # Check if the user is PMO
                ('project_manager', '=', current_user.employee_id.id),  # Check if the user is Project Manager
                ('department_manager_id', '=', current_user.employee_id.id),  # Check if the user is Department Manager
                ('team_lead_id', '=', current_user.employee_id.id),  # Check if the user is Team Lead
            ]

            # Count the number of projects based on the domain
            projects = self.env['project.project'].search(domain)
            # Set the computed field 'total_project' to the count of these projects
            self.total_project = len(projects)



    # Override the search method to apply domain filters based on user roles
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Get the current user
        current_user = self.env.user

        # If the user is an admin, they should see all projects
        if current_user.has_group('base.group_system'):
            return super(ProjectEnhancement, self).search(args, offset=offset, limit=limit, order=order, count=count)

        # If the user is not an admin, apply domain filter based on their roles
        domain = [
            '|', '|', '|',  # This represents OR conditions for each field
            ('pmo', '=', current_user.employee_id.id),  # Check if the user is PMO
            ('project_manager', '=', current_user.employee_id.id),  # Check if the user is Project Manager
            ('department_manager_id', '=', current_user.employee_id.id),  # Check if the user is Department Manager
            ('team_lead_id', '=', current_user.employee_id.id),  # Check if the user is Team Lead
        ]

        # Add the domain filter to the existing args and perform the search
        args = args + domain
        return super(ProjectEnhancement, self).search(args, offset=offset, limit=limit, order=order, count=count)



# Creating a logger board for logs for odoo14 - - -  Enable Logging on Model Fields
    # def write(self, vals):
    #     for record in self:
    #         changes = []
    #         for field_name, new_value in vals.items():
    #             old_value = record[field_name]
    #             if old_value != new_value:
    #                 changes.append(f"{field_name}: {old_value} -> {new_value}")
    #         if changes:
    #             _logger.info(f"User {self.env.user.name} modified {record.name}: {', '.join(changes)}")
    #     return super(ProjectEnhancement, self).write(vals)


# Changes on all fields in chatter logs
    def write(self, vals):
        for record in self:
            changes = []
            all_fields = record._fields  # This includes both default and custom fields

            for field_name, new_value in vals.items():
                if field_name not in all_fields:
                    continue  # Skip invalid fields

                old_value = record[field_name]

                # Handle Many2one fields
                if self._fields[field_name].type == 'many2one':
                    old_value = old_value.name if old_value else "None"
                    new_value = self.env[self._fields[field_name].comodel_name].browse(new_value).name if new_value else "None"

                # Handle Many2many & One2many fields
                elif self._fields[field_name].type in ['many2many', 'one2many']:
                    old_value = ", ".join(old_value.mapped('name')) if old_value else "None"
                    new_value = ", ".join(self.env[self._fields[field_name].comodel_name].browse(new_value).mapped('name')) if new_value else "None"

                # Handle Boolean fields
                elif isinstance(old_value, bool):
                    old_value = str(old_value)
                    new_value = str(new_value)

                # Ensure comparison works for all types
                if old_value != new_value:
                    changes.append(f"{field_name}: {old_value} -> {new_value}")
                    _logger.info(f"Field '{field_name}' changed from '{old_value}' to '{new_value}' in record ID {record.id}")

            if changes:
                message = _("Changes made: %s") % ", ".join(changes)
                record.message_post(body=message)  # Post changes in the chatter

        return super().write(vals)  # No need to specify ProjectProject, just use `super()`
    


    @api.model
    def create(self, vals):
        record = super(ProjectEnhancement, self).create(vals)
        _logger.info(f"User {self.env.user.name} created project {record.name} with values {vals}")
        return record


# Using the mail.message for a UI-based Log
    def write(self, vals):
        for record in self:
            changes = []
            for field_name, new_value in vals.items():
                old_value = record[field_name]
                if old_value != new_value:
                    changes.append(f"{field_name}: {old_value} -> {new_value}")
                    _logger.info(f"Field '{field_name}' changed from '{old_value}' to '{new_value}' in record ID {record.id}")

            if changes:
                message = _("Changes made: %s") % ", ".join(changes)
                record.message_post(body=message)

        return super(ProjectEnhancement, self).write(vals)
    

    # Enable Logging for create() & unlink()
    def create(self, vals):
        record = super(ProjectEnhancement, self).create(vals)
        _logger.info(f"New record created: {record.id} with values {vals}")
        return record

    def unlink(self):
        for record in self:
            _logger.info(f"Record deleted: {record.id}")
        return super(ProjectEnhancement, self).unlink()