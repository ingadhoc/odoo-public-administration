from openupgradelib import openupgrade
import logging
_logger = logging.getLogger(__name__)


# def migrate_payment_grup_note(env):
#     query = "select ap.id, notes from account_payment_group_bu apg join account_payment as ap on ap.payment_group_id_bu = apg.id where notes is not null"
#     openupgrade.logged_query(env.cr, query)
#     res = env.cr.fetchall()
#     for payment_id, note in res:
#         env['account.payment'].browse(payment_id).message_post(body='Nota migrada desde payment group version anterior: %s' % note)


def migrate_payment_grup_data(env):

    # mover campos (excepto m2m)
    # el campo state lo llevamos tmb porque en pay group tenian mas valores
    # de los nativos y queremos reflejarlo en el payment
    query = """
        update account_payment ap set
            advance_request_id = apg.advance_request_id,
            state = apg.state,
            reference = apg.reference,
            budget_id = apg.budget_id,
            expedient_id = apg.expedient_id,
            transaction_id = apg.transaction_id,
            transaction_with_advance_payment = apg.transaction_with_advance_payment,
            payment_base_date = apg.payment_base_date,
            payment_days = apg.payment_days,
            days_interval_type = apg.days_interval_type,
            payment_min_date = apg.payment_min_date,
            confirmation_date = apg.confirmation_date,
            to_signature_date = apg.to_signature_date
        from account_payment_group_bu as apg
        where
            ap.payment_group_id_bu = apg.id
        """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _logger.debug('Running migrate script for l10n_ar_withholding')
    migrate_payment_grup_data(env)
    # migrate_payment_grup_note(env)
