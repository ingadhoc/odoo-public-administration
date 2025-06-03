# Pre-migration script for adjusting account.payment.group.line linkage
# See requirements in user prompt

def migrate(cr, version):
    """
    - For each account.payment.group.line, find the related payment_group_id (old field)
    - Find the first account.payment with payment_group_id_bu = payment_group_id
    - Update account.payment.group.line to point to the payment (set payment_id)
    """

    # cr.execute("""
    #     SELECT id, payment_group_id
    #     FROM account_payment_group_line
    #     WHERE payment_group_id IS NOT NULL
    # """)
    # lines = cr.fetchall()
    # for line_id, payment_group_id in lines:
    #     # Find first payment for this group
    #     cr.execute("""
    #         SELECT id FROM account_payment
    #         WHERE payment_group_id_bu = %s
    #         ORDER BY id ASC
    #         LIMIT 1
    #     """, (payment_group_id,))
    #     payment = cr.fetchone()
    #     if payment:
    #         payment_id = payment[0]
    #         # Update line to point to payment
    #         cr.execute("""
    #             UPDATE account_payment_group_line
    #             SET payment_id = %s
    #             WHERE id = %s
    #         """, (payment_id, line_id))

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
