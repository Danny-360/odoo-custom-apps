# -*- coding: utf-8 -*-

from odoo import models, fields

class JournalRejectionReason(models.TransientModel):
    _name = "journal.rejection.reason"
    _description = "Journal Rejection Reason Wizard"

    journal_id = fields.Many2one('account.move', string="Journal Entry", default=lambda self: self.env.context.get('active_id', None), required=True)
    rejection_reason = fields.Char(string="Rejection Reason")

    def reject(self):
        # self.rma_id.rejection_reason = self.rejection_reason
        self.journal_id.with_context(warning=True).button_reject(self.rejection_reason)
