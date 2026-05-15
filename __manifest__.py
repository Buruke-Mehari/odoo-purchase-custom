{
    'name': 'Landed Cost Auto-Calculator',
    'version': '1.0',
    'category': 'Inventory/Purchase',
    'summary': 'Automatically creates Landed Costs from Purchase Order estimates upon receipt.',
    'description': """
        This module extends the Purchase and Inventory workflow:
        1. Adds Estimated Freight and Customs fields to Purchase Orders.
        2. Automatically generates Landed Cost records when a Receipt is validated.
        3. Updates the "True Cost" of products in real-time.
    """,
    'depends': [
        'base',
        'purchase',
        'stock',
        'stock_landed_costs',
    ],
    'data': [
       
        'views/purchase_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}