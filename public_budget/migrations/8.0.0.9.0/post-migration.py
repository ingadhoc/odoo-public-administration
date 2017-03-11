# -*- encoding: utf-8 -*-


def migrate(cr, version):
    print 'Migrating create_date to confirmation_date and validation date'
    if not version:
        return
    cr.execute(
        "DELETE FROM account_voucher_line WHERE id in ("
        "SELECT vl.id FROM account_voucher_line as vl "
        "INNER JOIN account_voucher as v on vl.voucher_id = v.id "
        "WHERE vl.amount = 0.0 and v.state != 'draft')"
    )
