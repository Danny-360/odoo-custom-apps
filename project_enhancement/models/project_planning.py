# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

#This adds a field to the Planning Module to select Projects, Tasks and Training IDs associated to a project during planning
class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    task_id = fields.Many2one('project.task', string="Project Task", domain="[('project_id', '=', project_id)]")
    project_id = fields.Many2one('project.project', string="Project ID", store=True, domain="[]")
    training_id = fields.Many2one('training.list', string="Training", store=True, domain="[]")

    #Extension for the selection fields of modules in planning
    # schedule_type = fields.Selection([
    #     ('project', 'Project'),
    #     ('training', 'training Management'),
    # ], string="Schedule Type", required=False, default='project')

    # record_id = fields.Many2one(
    #     'ir.model', string="Related Record",
    #     compute='_compute_record_id', store=False, readonly=False,
    #     domain="[]",
    #     help="This field dynamically fetches records based on the selected module.")

# @api.onchange('project_id')
# def _onchange_project_id(self):
#     """Clear the training field when a project is selected."""
#     if self.project_id:
#         # Clear the training_id field since the project is now selected
#         self.training_id = False
#         return {
#             'warning': {
#                 'title': "Notice",
#                 'message': "Training has been cleared because a project was selected."
#             }
#         }
#     else:
#         # Optionally handle the case where no project is selected
#         return {}


# @api.onchange('schedule_type')
# def _onchange_schedule_type(self):
#     """Dynamically show/hide fields based on schedule type."""
#     if self.schedule_type == 'project':
#         # Clear the training field and set a domain for project_id
#         self.training_id = False
#         return {
#             'domain': {'project_id': []},  # Add specific domain filters if needed
#             'warning': {'title': "Notice", 'message': "Please select a project."}
#         }
#     elif self.schedule_type == 'training':
#         # Clear the project field and set a domain for training_id
#         self.project_id = False
#         return {
#             'domain': {'training_id': []},  # Add specific domain filters if needed
#             'warning': {'title': "Notice", 'message': "Please select a training."}
#         }
#     else:
#         # Reset both fields if no valid schedule type is selected
#         self.project_id = False
#         self.training_id = False
#         return {}

# @api.depends('schedule_type', 'project_id', 'training_id')
# def _compute_related_record(self):
#     """Compute logic for other fields if needed."""
#     pass  # Placeholder for any further logic