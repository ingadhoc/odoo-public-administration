from odoo import models, fields, api


class BudgetModification(models.Model):

    _name = 'public_budget.budget_modification'
    _description = 'Budget Modification'

    date = fields.Date(
        required=True,
        default=fields.Date.context_today
    )
    initial_approval = fields.Boolean(
        string='Is Initial Approval?'
    )
    type = fields.Selection([
        ('increase_decrease', 'Increase / Decrease'),
        ('exchange', 'Exchange')],
        string='Budget Modification Type',
        required=True,
        default='increase_decrease'
    )
    name = fields.Char(
        required=True
    )
    reference = fields.Char(
        required=True
    )
    rest_message = fields.Char(
        string='Message',
        compute='_compute_restriction_data'
    )
    rest_type = fields.Many2one(
        'public_budget.rest_type',
        string='Restriction Type',
        compute='_compute_restriction_data'
    )
    budget_id = fields.Many2one(
        'public_budget.budget',
        required=True
    )
    budget_modification_detail_ids = fields.One2many(
        'public_budget.budget_modification_detail',
        'budget_modification_id',
        string='Details'
    )

    @api.depends(
        'budget_modification_detail_ids.budget_position_id',
        'budget_modification_detail_ids.amount',
    )
    def _compute_restriction_data(self):
        for rec in self:
            rest_message = False
            rest_type = False
            if rec.type == 'exchange':
                decrease_category_ids = [
                    x.budget_position_id.category_id.id for x in (
                        rec.budget_modification_detail_ids) if x.amount < 0.0]
                increase_category_ids = [
                    x.budget_position_id.category_id.id for x in (
                        rec.budget_modification_detail_ids) if x.amount > 0.0]
                domain = [('origin_category_id', 'in', decrease_category_ids),
                          ('destiny_category_id', 'in', increase_category_ids)]
                restrictions = rec.env[
                    'public_budget.budget_pos_exc_rest'].search(
                    domain + [('type', '=', 'block')])
                if not restrictions:
                    restrictions = rec.env[
                        'public_budget.budget_pos_exc_rest'].search(
                        domain + [('type', '=', 'alert')])

                rest_message = restrictions.message
                rest_type = restrictions.type
            rec.rest_message = rest_message
            rec.rest_type = rest_type

    @api.multi
    def unlink(self):
        """Si borramos una modification como se borran por cascade no se llama
        el unlink de los detail
        """
        to_check = []
        for rec in self.mapped('budget_modification_detail_ids'):
            to_check.append((
                rec.budget_position_id, rec.budget_modification_id.budget_id))
        res = super(BudgetModification, self).unlink()
        for position, budget in to_check:
            self.env['public_budget.budget_modification_detail'].\
                _check_modification(position, budget)
        return res
