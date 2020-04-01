from odoo import models, fields, api


class PublicBudgetAvanceRequestReportWizard(models.TransientModel):
    _name = "public_budget.advance.request.report.wizard"
    _description = "public_budget.advance.request.report.wizard"

    type_id = fields.Many2one(
        'public_budget.advance_request_type',
        string='Tipo',
        required=True,
    )
    to_date = fields.Date(
        'Hasta Fecha',
    )

    def confirm(self):
        self.ensure_one()
        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'advance_request_debt_report')],
            limit=1).with_context(
                to_date=self.to_date).report_action(self.type_id)
