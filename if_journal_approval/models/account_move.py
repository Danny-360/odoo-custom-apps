# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    need_approval = fields.Boolean(string='Approval needed')
    state = fields.Selection(selection_add=[
        ('submit', 'Finance Approval'),
        ('posted',),
        ('reject', 'Rejected')
    ],
        ondelete={'submit': 'set default',
                  'posted': 'set default', 'reject': 'set default'}
    )

    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
                               states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    invoice_date_due = fields.Date(string='Due Date', readonly=True, index=True, copy=False,
                                   states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})

    date = fields.Date(
        string='Date',
        required=True,
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]},
        copy=False,
        tracking=True,
        default=fields.Date.context_today
    )

    def button_submit(self):

        if self.move_type == 'in_invoice':
            approval_group = self.env.ref('if_journal_approval.group_finance_head')
            message = "Vendor Bill {} requires your Approval".format(self.name)
            partners_to_notify = self.env['res.partner'].sudo()
            for user in approval_group.users:
                partners_to_notify += user.partner_id
            self.notify_of_account_move(
                message=message, partner_ids=partners_to_notify.ids)
        elif self.move_type == 'in_receipt':
            approval_group = self.env.ref('if_journal_approval.group_finance_head')
            message = "Receipt {} requires your Approval".format(self.name)
            partners_to_notify = self.env['res.partner'].sudo()
            for user in approval_group.users:
                partners_to_notify += user.partner_id
            self.notify_of_account_move(
                message=message, partner_ids=partners_to_notify.ids)
        return self.write({'state': 'submit'})

    def button_submit_journal(self):
        if self.move_type == 'entry' and self.need_approval:
            approval_group = self.env.ref(
                'if_journal_approval.group_finance_head')
            message = "Journal Entry {} requires your Approval".format(self.name)
            partners_to_notify = self.env['res.partner'].sudo()
            for user in approval_group.users:
                partners_to_notify += user.partner_id
            self.notify_of_account_move(
                message=message, partner_ids=partners_to_notify.ids)
        return self.write({'state': 'submit'})

    def button_approve(self):
        if self.move_type == 'entry':
            message = "Journal Entry {} has been Approved & Posted".format(self.name)
        elif self.move_type == 'in_invoice':
            message = "Vendor Bill {} has been Approved & Posted".format(self.name)
        elif self.move_type == 'in_receipt':
            message = "Receipt {} has been Approved & Posted".format(self.name)
        partners_to_notify = self.message_partner_ids
        self.notify_of_account_move(
            message=message, partner_ids=partners_to_notify.ids)
        self.action_post()
        return True

    # def button_approve_internal(self):
    #     if self.move_type == 'entry':
    #         message = "Journal Entry {} has been Approved & Posted".format(self.name)
    #     elif self.move_type == 'in_invoice':
    #         approval_group = self.env.ref('filmhouse_journal_approval.group_approval_vendor_bill')
    #         message = "Vendor Bill {} requires your final Approval".format(self.name)
    #         partners_to_notify = self.env['res.partner'].sudo()
    #         for user in approval_group.users:
    #             partners_to_notify += user.partner_id
    #         self.notify_of_account_move(
    #             message=message, partner_ids=partners_to_notify.ids)
    #     elif self.move_type == 'in_receipt':
    #         approval_group = self.env.ref('filmhouse_journal_approval.group_approval_vendor_bill')
    #         message = "This Receipt {} requires your final Approval".format(self.name)
    #         partners_to_notify = self.env['res.partner'].sudo()
    #         for user in approval_group.users:
    #             partners_to_notify += user.partner_id
    #         self.notify_of_account_move(
    #             message=message, partner_ids=partners_to_notify.ids)
    #     return self.write({'state': 'finance'})

    def button_reject(self, reason):
        message = "Journal Entry {} has been rejected, Reason: {}".format(self.name, reason)
        partners_to_notify = self.message_partner_ids
        self.notify_of_account_move(
            message=message, partner_ids=partners_to_notify.ids)
        self.state = 'reject'
        return True

    def button_reset(self):
        self.state = 'draft'

    def notify_of_account_move(self, message=None, partner_ids=[]):
        if not (message and partner_ids):
            return
        self.message_subscribe(partner_ids=partner_ids)
        self.message_post(subject=message, body=message,
                          partner_ids=partner_ids, subtype_xmlid="mail.mt_comment")
        return True

