from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    notify_md = fields.Boolean(string="Notify MD", default=False)

    def action_validate(self):
        res = super(HrLeave, self).action_validate()
        for leave in self:
            if leave.state == 'validate' and leave.notify_md:
                self._send_md_notification(leave)
        return res

    def _send_md_notification(self, leave):
        md_group = self.env.ref('dubri_leave_extension.managing_director_group')
        if not md_group:
            return
        md_users = md_group.users
        email_template = self.env.ref('dubri_leave_extension.email_template_md_notification')
        for user in md_users:
            email_template.send_mail(leave.id, email_values={'email_to': user.email})

