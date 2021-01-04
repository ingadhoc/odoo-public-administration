{
    'name': 'Public Budget',
    'license': 'AGPL-3',
    'version': "13.0.1.11.0",
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'depends': [
        'portal_backend',
        'sales_team',
        'account_accountant_ux',
        'account_check',
        'account_payment_group',
        'account_payment_group_document',
        'account_asset',
        'hr_holidays_public',
        'report_aeroo',
        'account_statement_aeroo_report',
        # estrictamente solo requerido por algunos campos en vista de partner
        # solo requerido para establecer datos demo en cia y hacer que las ret
        # no sean obligatorias en borrador
        'l10n_ar_account_withholding',
        # usado por algunos reportes como el de cheques y retenciones
        'l10n_ar_ux',
        # Para poder habilitar el cancel_invoice en estado hecho para todos los
        # users sin modo desarrollador
        'account_ux',
        'web_ir_actions_act_multi',
    ],
    'data': [
        'security/public_budget_group.xml',
        'security/ir.model.access.csv',
        'security/public_budget_security.xml',
        'security/hide_groups.xml',
        'wizards/transaction_definitive_make_invoice_views.xml',
        'wizards/transaction_definitive_mass_invoice_create_views.xml',
        'wizards/budget_analysis_wizard_views.xml',
        'wizards/avance_request_report_wizard_views.xml',
        'wizards/public_budget_preventive_changeposition_views.xml',
        'wizards/account_check_debit_views.xml',
        'wizards/transfer_asset_wizard_views.xml',
        'reports/advance_request_analysis_view.xml',
        'reports/public_budget_budget_report_view_4.xml',
        'reports/stylesheet.xml',
        'reports/payment_order_report.xml',
        'reports/remit_report.xml',
        'reports/expedient_report.xml',
        'reports/transaction_report.xml',
        'reports/payment_receipt_report.xml',
        'reports/statement_report.xml',
        'reports/budget_report_excel.xml',
        'reports/budget_report.xml',
        'reports/advance_request_report.xml',
        'reports/advance_return_report.xml',
        'reports/liquidation_report.xml',
        'reports/advance_request_debt_report.xml',
        'reports/asset_report.xml',
        'reports/asset_report_excel.xml',
        'reports/asset_report_baja.xml',
        'reports/asset_report_alta.xml',
        'reports/asset_amend_report.xml',
        'reports/asset_missing_report.xml',
        'reports/asset_report_printing.xml',
        'reports/check_report.xml',
        'reports/payment_order_list.xml',
        # 'reports/public_budget_budget_report_view_3.xml',
        'reports/budget_modification_report.xml',
        'reports/payment_list_report.xml',
        'views/account_move_views.xml',
        'views/inventory_rule_views.xml',
        'views/advance_request_type_views.xml',
        'views/advance_request_views.xml',
        'views/transaction_type_views.xml',
        'views/transaction_type_amo_rest_views.xml',
        'views/advance_return_views.xml',
        'views/expedient_category_views.xml',
        'views/location_views.xml',
        'views/budget_modification_detail_views.xml',
        'views/funding_move_views.xml',
        'views/account_move_line_views.xml',
        'views/rest_type_views.xml',
        'views/res_users_views.xml',
        'views/preventive_line_views.xml',
        'views/budget_position_views.xml',
        'views/res_company_views.xml',
        'views/budget_detail_views.xml',
        'views/budget_prec_detail_views.xml',
        'views/transaction_views.xml',
        'views/budget_position_category_views.xml',
        'views/budget_views.xml',
        'views/remit_views.xml',
        'views/budget_pos_exc_rest_views.xml',
        'views/budget_modification_views.xml',
        'views/expedient_founder_views.xml',
        'views/res_partner_views.xml',
        'views/account_asset_views.xml',
        'views/account_check_views.xml',
        'views/account_payment_group_views.xml',
        'views/account_payment_views.xml',
        'views/hr_public_holidays_views.xml',
        'views/custom_views.xml',
        'views/public_budget_menuitem.xml',
        'views/definitive_line_views.xml',
        'views/expedient_views.xml',
        'views/public_budget_actions.xml',
        'views/account_checkbook_views.xml',
        'views/account_journal_views.xml',
        'data/sequence.xml',
        'data/expedient_category.xml',
        'data/expedient_founder.xml',
        'data/position_category.xml',
        'data/position_exc_restrictions.xml',
        'data/ir_config_parameter_data.xml',
        'data/server_actions_data.xml',
    ],
    'demo': [
        'demo/res_company_demo.xml',
        'demo/public_budget.location.csv',
        'demo/res_users_demo.xml',
        # once admin is in sipreco company, we load chart of account
        'demo/account_chart_template.xml',
        'demo/res_partner_demo.xml',
        'demo/res.partner.csv',
        'demo/account_account_demo.xml',
        'demo/account_payment_receiptbook_demo.xml',
        'demo/public_budget.transaction_type.csv',
        'demo/public_budget.expedient.csv',
        'demo/public_budget.budget_position.csv',
        'demo/public_budget.budget.csv',
        'demo/public_budget.budget_detail.csv',
        'demo/public_budget_transaction_demo.xml',
        'demo/public_budget.preventive_line.csv',
        'demo/public_budget_definitive_line_demo.xml',
        'demo/public_budget.remit.csv',
        'demo/public_budget.budget_modification.csv',
        'demo/public_budget.budget_modification_detail.csv',
        'demo/account_journal_demo.xml',
        'demo/advance_request_type.xml',
        'demo/advance_request.xml',
    ],
    'installable': True,
}
