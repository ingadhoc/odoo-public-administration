from odoo import api, models, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    advance_request_debt = fields.Monetary(
        compute='_compute_advance_request_debt',
    )
    # TODO ver si en v10 convertimos esto a un document id del partner
    numero_legajo = fields.Char(
    )
    subsidy_recipient = fields.Boolean(
    )
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
    )
    drei_number = fields.Char(
    )
    # por defecto prefieren que sea esta opción para poder poner otros
    # domicilios
    type = fields.Selection(
        default='other',
    )
    supplier = fields.Boolean(
        compute="_compute_supplier",
        inverse="_set_supplier",
    )

    def mark_as_reconciled(self):
        # run with sudo because it gives error if you dont have rights to write
        # on partner
        return super(ResPartner, self.sudo()).mark_as_reconciled()

    def _compute_advance_request_debt(self):
        advance_return_type = self.env[
            'public_budget.advance_request_type'].browse(self._context.get(
                'advance_return_type_id', False))
        for rec in self:
            rec.advance_request_debt = rec.get_debt_amount(
                advance_return_type)

    def get_debt_amount(self, advance_return_type=False, to_date=False):
        self.ensure_one()
        requested_domain = [
            ('employee_id', '=', self.id),
            ('advance_request_id.state', 'not in', ['draft', 'cancel']),
        ]
        returned_domain = [
            ('employee_id', '=', self.id),
            ('advance_return_id.state', 'not in', ['draft', 'cancel']),
        ]

        if advance_return_type:
            requested_domain.append(
                ('advance_request_id.type_id', '=', advance_return_type.id))
            returned_domain.append(
                ('advance_return_id.type_id', '=', advance_return_type.id))

        if to_date:
            requested_domain.append(
                ('advance_request_id.approval_date', '<=', to_date))
            returned_domain.append(
                ('advance_return_id.confirmation_date', '<=', to_date))

        requested_amount = sum(
            self.env['public_budget.advance_request_line'].search(
                requested_domain).mapped('approved_amount'))
        returned_amount = sum(
            self.env['public_budget.advance_return_line'].search(
                returned_domain).mapped('returned_amount'))
        return requested_amount - returned_amount

    @api.depends('supplier_rank')
    def _compute_supplier(self):
        for rec in self:
            rec.supplier = True if rec.supplier_rank > 0 else False

    def _set_supplier(self):
        for rec in self:
            rec.supplier_rank = 1 if rec.supplier else 0
