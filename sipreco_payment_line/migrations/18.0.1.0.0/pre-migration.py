# Pre-migration script for adjusting account.payment.group.line linkage
# See requirements in user prompt
from openupgradelib import openupgrade


def migrate(cr, version):
    """
    - For each account.payment.group.line, find the related payment_group_id (old field)
    - Find the first account.payment with payment_group_id_bu = payment_group_id
    - Update account.payment.group.line to point to the payment (set payment_id)
    """

    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE account_payment_group_line
        ADD COLUMN IF NOT EXISTS payment_id int4
        """,
    )

    cr.execute('''
        UPDATE account_payment_group_line l
        SET payment_id = p.id
        FROM (
            SELECT DISTINCT ON (payment_group_id_bu) id, payment_group_id_bu
            FROM account_payment
            WHERE payment_group_id_bu IS NOT NULL
            ORDER BY payment_group_id_bu, id ASC
        ) p
        WHERE l.payment_group_id = p.payment_group_id_bu
          AND l.payment_group_id IS NOT NULL
    ''')
