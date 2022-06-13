# -*- coding: utf-8 -*-

{
    'name': "Approvals Statement",
    'version': '1.3',
    'depends': ['account_accountant'],
    'author': "Sebastien Buhl",
    'website': "http://www.buhl.be",
    'license': 'LGPL-3',
    'application': True,
    'category': 'Customizations',
    'summary': 'Statements Approvals',
    'description': """
        Add an approval field on the bank statement
            note that the field is only informative
        Add a group Sales Level
        Only Store Manager can approve Bank Statement
    """,
    'data': [
        'data/activity.xml',
        'views/account_approval_request_inherited_tree.xml',
        'security/security.xml',
    ],
}
