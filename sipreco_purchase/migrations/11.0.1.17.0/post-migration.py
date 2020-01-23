from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info(
        'Compute the field user_confirm with the user who confirm')
    for line in env['purchase.order'].search(
            [('state', 'in', ['to_approve', 'purchase'])]):
        value = line.message_ids.mapped('tracking_value_ids').filtered(
            lambda x: x.field == 'state' and x.new_value_char == 'Pedido de compra')
        if len(value) == 1:
            line.write(
                {'user_confirmed_id': value.mail_message_id.author_id.user_ids
                 and value.mail_message_id.author_id.user_ids[0].id})
