from odoo import api, fields, models, _


class HospitalServiceCheckup(models.Model):
    _name = 'hospital.service.checkup'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Service Check Up'
    
    service_reference = fields.Char(string="Reference", required=True, copy=False, readonly=True, 
                                    default=lambda self: _('New'))
    name = fields.Char(string='Name')
    price = fields.Integer(string='Price')
    note = fields.Char(string='Description')

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = "New Service Checkup"
        if vals.get('service_reference', ('New')) == ('New'):
            vals['service_reference'] = self.env['ir.sequence'].next_by_code('hospital.service.checkup') or ('New')
        res = super(HospitalServiceCheckup, self).create(vals)
        return res
    
    
