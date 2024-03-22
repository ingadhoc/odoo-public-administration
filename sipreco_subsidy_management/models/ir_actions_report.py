from odoo import models
from odoo.exceptions import UserError

class IrActionsReport(models.Model):

    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        pdf_content, report_type = super(IrActionsReport, self)._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
        report_sudo = self._get_report(report_ref)

        if res_ids and report_sudo.model == 'helpdesk.ticket':
            helpdesk_ticket_model = self.env['helpdesk.ticket']
            helpdesk_ticket = helpdesk_ticket_model.browse(res_ids)
            dni_values = [ticket.dni for ticket in helpdesk_ticket if ticket.dni]

            if len(dni_values) != len(set(dni_values)):
                raise UserError("No puede haber 2 o más DNI/CUIT iguales en la misma resolución")

        return pdf_content, report_type
