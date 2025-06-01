import json
from odoo import models, fields, api
from odoo.exceptions import UserError

class RoleAssignmentWizard(models.TransientModel):
    _name = 'role.assignment.wizard'
    _description = 'Role Assignment Wizard'

    project_id = fields.Many2one('project.project', string='Project', store=True)
    role = fields.Selection([('project_manager', 'Project Manager'),
                             ('team_lead', 'Team Lead'),
                             ('department_manager', 'Department Manager')], string='Role', store=True)
    response = fields.Selection([('accepted', 'Accepted'), ('declined', 'Declined')], string='Response', store=True)
    decline_reason = fields.Text(string="Decline Reason", store=True)
    assigned_by = fields.Many2one('hr.employee', string='Assigned By', store=True)

    @api.model
    def default_get(self, fields):
        res = super(RoleAssignmentWizard, self).default_get(fields)

        # Retrieve context parameters and use them to auto-populate the fields
        context_string = self.env.context.get('context', '{}')
        
        try:
            context_dict = json.loads(context_string)  # Safe parsing using json
        except json.JSONDecodeError:
            context_dict = {}

        # If project_name is passed in the context, find the project and update the project_id field
        project_name = context_dict.get('project_name')
        role = context_dict.get('role')
        assigned_by_id = context_dict.get('assigned_by')

        if project_name:
            project = self.env['project.project'].search([('name', '=', project_name)], limit=1)
            if project:
                res.update({'project_id': project.id})

                # Check if the role has already been accepted or declined
                if project.role_accepted or project.role_declined:
                    raise UserError("This role has already been accepted or declined. No further actions can be taken.")

        # Update the role field if it's passed in the context
        if role:
            res.update({'role': role})

        # Update the assigned_by field based on the assigned_by_id passed in the context
        if assigned_by_id:
            assigned_by = self.env['hr.employee'].browse(assigned_by_id)
            if assigned_by:
                res.update({'assigned_by': assigned_by.id})

        return res

    def action_submit(self):
        """Handle the role acceptance or decline action."""
        project = self.project_id
        assigned_by = self.assigned_by  # The person who assigned the role is now in the 'assigned_by' field

        if project.role_accepted or project.role_declined:
            raise UserError("This role has already been accepted or declined. No further actions can be taken.")
        
        if self.response == 'declined':
            # Ensure the decline reason is provided
            if not self.decline_reason:
                raise UserError("You must provide a reason for declining the role.")

            # Revoke the role assignment from the project
            if self.role == 'project_manager':
                project.write({'project_manager': False})
            elif self.role == 'team_lead':
                project.write({'team_lead_id': False})
            elif self.role == 'department_manager':
                project.write({'department_manager_id': False})

            # Mark the role as declined
            project.write({'role_declined': True})

            # Send email notification to assigned_by when the role is declined
            subject = f"Role Declined: {project.name} - {self.role}"
            body_html = f"""
                <p>Hello {assigned_by.name},</p>
                <p>The user {self.env.user.name} has declined the role of {self.role} for project {project.name}.</p>
                <p>Reason: {self.decline_reason}</p>
            """
            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_to': assigned_by.work_email,  # Send email to the person who assigned the role
            }
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

            # After the decline and email, close the wizard.
            return {'type': 'ir.actions.act_window_close'}

        elif self.response == 'accepted':
            # Mark the role as accepted
            if self.role == 'project_manager':
                project.write({'project_manager': self.env.user.id})
            elif self.role == 'team_lead':
                project.write({'team_lead_id': self.env.user.id})
            elif self.role == 'department_manager':
                project.write({'department_manager_id': self.env.user.id})

            project.write({'role_accepted': True})

            # Send a notification to the assigned_by when the role is accepted
            subject = f"Role Accepted: {project.name} - {self.role}"
            body_html = f"""
                <p>Hello {assigned_by.name},</p>
                <p>The user {self.env.user.name} has accepted the role of {self.role} for project {project.name}.</p>
            """
            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_to': assigned_by.work_email,  # Send email to the person who assigned the role
            }
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

            # Redirect to the project form view
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'view_mode': 'form',
                'view_id': self.env.ref('project.edit_project').id,
                'res_id': project.id,
                'target': 'current',
            }

        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        """Handle the cancel action and close the wizard."""
        return {'type': 'ir.actions.act_window_close'}
