# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ISPInvoice(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_invoice_module.invoice"
    _description = "ISP Invoices"

    name = fields.Char('Name', required=True, translate=True)

