from odoo import models, fields


class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    activity_ids = fields.One2many(
        groups="base.group_user, base.group_portal",
    )
    activity_state = fields.Selection(
        groups="base.group_user, base.group_portal",
    )
    activity_user_id = fields.Many2one(
        groups="base.group_user, base.group_portal",
    )
    activity_type_id = fields.Many2one(
        groups="base.group_user, base.group_portal",
    )
    activity_date_deadline = fields.Date(
        groups="base.group_user, base.group_portal",
    )
    activity_summary = fields.Char(
        groups="base.group_user, base.group_portal",
    )
