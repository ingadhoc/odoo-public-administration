# -*- encoding: utf-8 -*-


def migrate(cr, version):
    print 'Migrating create_date to confirmation_date and validation date'
    if not version:
        return
    table = 'public_budget_advance_request'
    source_field = "create_date"
    target_field = "approval_date"
    condition = "state NOT IN ('cancel', 'draft')"
    cr.execute(
        "UPDATE %s SET %s = %s WHERE %s" % (
            table, target_field, source_field, condition))

    target_field = "confirmation_date"
    cr.execute(
        "UPDATE %s SET %s = %s WHERE %s" % (
            table, target_field, source_field, condition))

    table = 'public_budget_advance_return'
    target_field = "confirmation_date"
    cr.execute(
        "UPDATE %s SET %s = %s WHERE %s" % (
            table, target_field, source_field, condition))
