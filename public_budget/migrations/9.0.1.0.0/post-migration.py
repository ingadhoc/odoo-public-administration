# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# from openerp.api import Environment
try:
    from openupgradelib.openupgrade_tools import table_exists
    from openupgradelib import openupgrade
except ImportError:
    table_exists = None
import logging
from openerp.exceptions import ValidationError
_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    """
    El campo reference no lo tenemos en los payment groups, lo agregamos
    con sipreco. Odoo lo migro de los vouchers a payment_reference en odoo
    pero no se usa practicamente, lo movemos al campo que generamos para
    sipreco en payment group.
    Ademas, odoo lleva el campo name de voucher a name de payment pero si
    name en payment seria la secuencia y en realidad communication esta vacio,
    como usamos com.. para reemplazar name, copiamos names viejos a com..

    IMPORTANTE No buscamos por diario porque podria haber cambiado con cheques
    """
    correct_advance_account_types(env)
    cr = env.cr

    cr.execute("""
        SELECT confirmation_date, partner_id, name, create_date, create_uid,
            reference, transaction_id, expedient_id, advance_request_id,
            payment_base_date, payment_days, number, state, move_id, date,
            amount
        FROM account_voucher_copy
        /*WHERE confirmation_date is not null*/
        """,)

    reads = cr.fetchall()
    for read in reads:
        (
            confirmation_date,
            partner_id,
            name,
            create_date,
            create_uid,
            reference,
            transaction_id,
            expedient_id,
            advance_request_id,
            payment_base_date,
            payment_days,
            number,
            state,
            move_id,
            date,
            amount) = read

        # si no hay asiento que vincule, entonces tratamos
        # tratamos de buscar algo unico para vincular el voucher con el payment
        if move_id:
            domain = [('move_id', '=', move_id), ('payment_id', '!=', False)]
            payment = env[('account.move.line')].search(domain).mapped(
                'payment_id')
        else:
            # si no tiene move id entonces no esta confirmado
            domain = [
                ('partner_id', '=', partner_id),
                ('create_date', '=', create_date),
                ('create_uid', '=', create_uid),
                ('payment_reference', '=', reference),
                # usamos abs porque pagos negativos se convirtieron a positivo
                ('amount', '=', abs(amount)),
                ('state', 'not in', ('posted', 'sent', 'reconciled')),
            ]
            payment = env['account.payment'].search(domain)

            # si nos devuelve mas de uno intentamos agregar condición de name
            # no lo hacemos antes ya que en otros casos no sirve
            if len(payment) > 1 and name:
                domain.append(('name', '=', name))
                payment = env['account.payment'].search(domain)

        if len(payment) != 1:
            raise ValidationError(
                'Se encontro mas de un payment o ninguno!!! \n'
                '* Payments: %s\n'
                '* Domain: %s' % (payment, domain))

        if not payment.payment_group_id:
            _logger.error(
                'No encontramos payment group para payment %s' % (payment))
            continue
        _logger.info('Seteando fecha de payment group %s' % payment)

        vals = {
            'confirmation_date': confirmation_date,
            'reference': reference,
            'communication': name,
            'transaction_id': transaction_id,
            'expedient_id': expedient_id,
            'advance_request_id': advance_request_id,
            'payment_base_date': payment_base_date,
            'payment_days': payment_days,
        }

        # solo actualizamos estado si esta en alguno de los nuevos, el resto
        # ya estaria bien
        if state in ['confirmed', 'signature_process', 'signed']:
            vals['state'] = state

        # odoo cuando migra a ap, si no habia date le pone la fecha de creacion
        # en payment date ya que era requerido, nosotrols lo hicimos
        # no requeridos y queremos matener el false porque si no, ademas
        # tenemos error de constrain
        if not date and payment.payment_date:
            payment.payment_date = False
            vals['payment_date'] = False
        # no es necesario porque lo arreglamos en la v8
        # else:
        #     vals['payment_date'] = date
        payment.payment_group_id.write(vals)


def correct_advance_account_types(env):
    accounts = env['public_budget.transaction_type'].search(
        [('advance_account_id', '!=', False)]).mapped('advance_account_id')
    accounts.write({
        'reconcile': False,
        'user_type_id': env.ref('account.data_account_type_liquidity').id,
    })
