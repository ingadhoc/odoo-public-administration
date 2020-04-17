from odoo import models, fields


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    message_attachment_count = fields.Integer(
        groups="base.group_user, base.group_portal")
