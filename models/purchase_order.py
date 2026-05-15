from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    est_freight_amt = fields.Monetary(string="Estimated Freight")
    est_customs_amt = fields.Monetary(string="Estimated Customs")

    landed_cost_method = fields.Selection([
    ('equal', 'Equal'),
    ('by_quantity', 'By Quantity'),
    ('by_current_cost_price', 'By Current Cost'), # <--- Must be exactly this
    ('by_weight', 'By Weight'),
    ('by_volume', 'By Volume'),
], string="Split Method", default='equal')

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        # Execute standard validation
        res = super(StockPicking, self).button_validate()

        for picking in self:
            # Check if it's an incoming shipment linked to a PO
            if picking.state == 'done' and picking.picking_type_code == 'incoming' and picking.purchase_id:
                po = picking.purchase_id
                if po.est_freight_amt > 0 or po.est_customs_amt > 0:
                    picking._create_automated_landed_costs(po)
        return res

    def _create_automated_landed_costs(self, po):
        # Find the Landed Cost product (ensure you have one for Freight and one for Customs)
        # Or use a generic one for this example
        landed_product = self.env['product.product'].search([('landed_cost_ok', '=', True)], limit=1)
        
        if not landed_product:
            return False

        cost_lines = []
        
        # Add Freight Line
        if po.est_freight_amt > 0:
            cost_lines.append((0, 0, {
                'name': _('Auto Freight: %s') % po.name,
                'product_id': landed_product.id,
                'price_unit': po.est_freight_amt,
                'split_method': po.landed_cost_method,
                'account_id': landed_product.property_account_expense_id.id or 
                              landed_product.categ_id.property_account_expense_categ_id.id,
            }))

        # Add Customs Line
        if po.est_customs_amt > 0:
            cost_lines.append((0, 0, {
                'name': _('Auto Customs: %s') % po.name,
                'product_id': landed_product.id,
                'price_unit': po.est_customs_amt,
                'split_method': po.landed_cost_method,
                'account_id': landed_product.property_account_expense_id.id or 
                              landed_product.categ_id.property_account_expense_categ_id.id,
            }))

        if cost_lines:
            landed_cost = self.env['stock.landed.cost'].create({
                'picking_ids': [(4, self.id)],
                'cost_lines': cost_lines,
            })
            
            # Compute and Validate
            landed_cost.compute_landed_cost()
            landed_cost.button_validate()