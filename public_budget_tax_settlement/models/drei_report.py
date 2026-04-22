# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import UserError


class L10n_ArDreiReportHandler(models.AbstractModel):
    _name = "l10n_ar.drei.report.handler"
    _inherit = ["account.tax.report.handler"]
    _description = "Argentinian DREI Report Custom Handler"

    def _custom_options_initializer(self, report, options, previous_options):
        super()._custom_options_initializer(report, options, previous_options=previous_options)

        # Add export button
        txt_export_button = [
            {
                "name": "TXT Retenciones DREI",
                "sequence": 30,
                "action": "export_file",
                "action_param": "drei_ret_perc_txt",
                "file_export_type": "TXT",
                "branch_allowed": True,
            },
        ]
        options["buttons"].extend(txt_export_button)

    def drei_ret_perc_txt(self, options):
        return {
            "file_name": "DREI retenciones aplicadas.txt",
            "file_content": self._drei_get_txt_files(options),
            "file_type": "txt",
        }

    def _drei_get_txt_files(self, options):
        """Returns DREI txt content"""
        move_lines = self._drei_get_txt_lines(options)
        return "".join(self._get_drei_txt_content(move_lines)).encode("ISO-8859-1", "ignore")

    def get_standard_lines_domain(self, company_ids, options):
        domain = [("company_id", "in", company_ids)]
        state = options.get("all_entries") and "all" or "posted"
        if state and state.lower() != "all":
            domain += [("move_id.state", "=", state)]
        if options.get("date").get("date_to"):
            domain += [("date", "<=", options["date"]["date_to"])]
        if options.get("date").get("date_from"):
            domain += [("date", ">=", options["date"]["date_from"])]
        return domain

    def _drei_get_txt_lines(self, options):
        state = options.get("all_entries") and "all" or "posted"
        if state != "posted":
            raise UserError(
                _(
                    "Can only generate TXT files using posted entries."
                    " Please remove Include unposted entries filter and try again"
                )
            )
        domain = [
            ("tax_line_id.l10n_ar_state_id.country_id.code", "=", "AR"),
            ("tax_line_id.l10n_ar_withholding_payment_type", "=", "supplier"),
            # mejorar esto del domain para que no dependa del nombre del grupo de impuestos,
            # sino de alguna característica más técnica
            ("tax_line_id.tax_group_id.name", "=", "Retención DreI"),
            ("payment_id", "!=", False),
        ] + self.get_standard_lines_domain(self.env.company.ids, options)
        return self.env["account.move.line"].search(domain, order="date asc, name asc, id asc")

    def _get_drei_txt_content(self, move_lines):
        """Implementado según especificación indicada en ticket 39347. También se puede ver detalles en readme"""
        lines = []
        for line in move_lines.sorted(key=lambda r: (r.date, r.id)):
            content = ""
            date = line.payment_id.date
            # cuit (req): 11
            content += line.partner_id.ensure_vat()
            # razon_soc (req): 80
            content += line.partner_id.name.ljust(80)[:80]
            # nro_certificado: 10
            content += "%010d" % int(line.withholding_id.name)
            # fecha_ret: 10 (formato "dd/mm/aaaa")
            content += fields.Date.from_string(date).strftime("%d/%m/%Y")
            # base_imp: 09.2
            content += "%012.2f" % line.withholding_id.base_amount
            tax = line._get_settlement_tax() or line.tax_line_id
            # alicuota: 09.6
            content += f"{tax.amount:0>16.6f}"
            # importe (req): 09.2
            content += "%012.2f" % abs(line.amount_currency)

            # new line
            content += "\r\n"
            lines.append(content)
        return lines
