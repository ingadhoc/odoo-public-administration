import logging
import base64
import io
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError as UserError

_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class AccountPaymentGroupLineImport(models.TransientModel):
    _name = 'account.payment.group.line.import'
    _description = 'Account Payment Lines Import'

    data_file = fields.Binary(
        'Archivo de Pago',
        required=True,
    )

    @api.multi
    def import_file(self):
        self.ensure_one()
        data_file = base64.b64decode(self.data_file)
        self._import_file(data_file)

    @api.model
    def _import_file(self, data_file):
        payment_lines = self.env['account.payment.group.line']
        payment_lines_vals = self._parse_file(data_file)
        self._check_parsed_data(payment_lines_vals)
        for payment_line_vals in payment_lines_vals:
            payment_lines += self._import_payment_lines(payment_line_vals)
        return payment_lines

    @api.model
    def _import_payment_lines(self, payment_line_vals):
        cuit = payment_line_vals.pop('cuit')
        partner = self._find_partner(cuit)
        if not partner and cuit:
            raise UserError(
                _('No se pudo encontrar partner para cuit %s.') % cuit
            )

        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_model != 'account.payment.group':
            raise UserError(
                _('No se está ejecutando el asistente desde un pago.')
            )
        if not active_id:
            raise UserError(
                _('No se encontró un pago activo en el contexto.')
            )
        payment_group = self.env[active_model].browse(active_id)
        # check if line already exist
        vals = {
            'cuit': cuit,
            'partner_id': partner.id,
            'bank_account_id': (
                partner.bank_ids and partner.bank_ids[0].id or False),
            'payment_group_id': payment_group.id,
            'amount': payment_line_vals.get('amount'),
        }
        payment_line = self.env['account.payment.group.line'].search([
            ('cuit', '=', cuit),
            ('payment_group_id', '=', payment_group.id)], limit=1)
        if payment_line:
            payment_line.write(vals)
        else:
            payment_line = payment_line.create(vals)
        return payment_line

    @api.model
    def _parse_file(self, data_file):
        res = []
        try:
            # skip first line
            for line in io.BytesIO(data_file).readlines()[1:]:
                _logger.info('Parsing line "%s"' % line)
                line_vals = line.decode('utf-8').split()
                try:
                    float(line_vals[4].strip())
                except ValueError:
                    _logger.warning(
                        "Could not get value from line %s" % line_vals)
                res.append({
                    'cuit': line_vals[1],
                    'amount': float(line_vals[4].strip())
                })
        except Exception as e:
            raise UserError(_(
                "Ocurrió un error al importar. "
                "El archivo puede no ser valido.\n\n %s" % e))
        return res

    @api.model
    def _check_parsed_data(self, payment_lines):
        # pylint: disable=no-self-use
        """ Basic and structural verifications """
        if len(payment_lines) == 0:
            raise UserError(_('This file doesn\'t contain any line.'))

    @api.model
    def _find_partner(self, cuit):
        return self.env['res.partner'].search([
            ('main_id_category_id.afip_code', '=', 80),
            ('main_id_number', '=', cuit),
        ], limit=1)
