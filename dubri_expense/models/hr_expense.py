from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    state = fields.Selection(selection_add=[
        ('manager_approved', "Manager Approved"),
        ('cos_head_approved', "Awaiting Corp Head Approval"),
        ('cos_approved', "Corporate Service Approved"),
        ('finance_approved', "Awaiting Finance Approval"),  # New Step
        ('md_approved', "MD Approved"),
        ('approve', ),
    ], ondelete={'manager_approved': 'set default', 'finance_approved': 'set default', 'cos_head_approved': 'set default', 'cos_approved': 'set default', 'md_approved': 'set default',})

    # req_md = fields.Boolean("Requires MD's Approval", default=False)

    def _do_approve(self):
        body = _(
            'Expense request %s has been approved by the Line manager but requires Corporate Service review and approval' % (
                self.name))
        self.notify(
            body=body, group='dubri_expense.corporate_service_user')
        emp = self.env['hr.employee'].search(
            [('user_id', '=', self._uid)], limit=1)

        self.state = "manager_approved"
    


    def cos_approve_sheet(self): #New
        """ Corporate Service Approval -> Forward to Finance """
        body = _(
            'Expense request %s has been approved by Corporate Service but requires Finance approval.' % self.name
        )
        self.notify(body=body, group='dubri_expense.finance_user')
        return self.write({"state": "finance_approved"})
    


    def action_finance_approve_sheet(self): #New
        """ Finance Approval -> Forward to Corporate Service Head """

        # Ensure only users in the Finance group can approve
        if not self.env.user.has_group('dubri_expense.finance_user'):
            raise UserError(_("You do not have permission to approve as Finance."))
    
        body = _(
            'Expense request %s has been approved by Finance but requires final approval from the Head of Corporate Service.' % self.name
        )
        self.notify(body=body, group='dubri_expense.head_corporate_service')
        return self.write({"state": "cos_head_approved"})
        # else:
        #     body = _(
        #         'Expense request %s has been approved by Corporate Service for payment processing by finance .' % (
        #             self.name))
        #     self.notify(
        #         body=body, group='account.group_account_manager')
        #     emp = self.env['hr.employee'].search(
        #         [('user_id', '=', self._uid)], limit=1)
        #     return self.write({"state": "approve"})

    def md_approve_sheet(self):
        body = _(
            'Expense request %s has been approved by the head of Corporate Service for payment processing .' % (
                self.name))
        self.notify(
            body=body, group='account.group_account_invoice')
        emp = self.env['hr.employee'].search(
            [('user_id', '=', self._uid)], limit=1)
        self.state = "approve"


    def notify(self, body='', users=[], group=False):
        post_msg = []
        if group:
            users = self.env['res.users'].search(
                [('active', '=', True), ('company_id', '=', self.env.user.company_id.id)])
            for user in users:
                if user.has_group(group) and user.id != 1:
                    post_msg.append(user.partner_id.id)
        else:
            post_msg = users
        if len(post_msg):
            self.message_post(body=body, partner_ids=post_msg)
        return True


