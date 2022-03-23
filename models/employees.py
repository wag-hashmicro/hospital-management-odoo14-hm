from odoo import api, fields, models, _


class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Doctor'
    _rec_name = 'doctor_name'

    doctor_reference = fields.Char(string="Doctor Reference", 
									required=True, copy=False, readonly=True,
									default=lambda self: _('New'))
    
    doctor_name = fields.Char(string='Name', required=True, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    specialist = fields.Char(string='Specialist')    
    gender = fields.Selection(string='Gender', selection=[
        ('male', 'Male'), 
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='male', tracking=True)
    note = fields.Text(string='Description')
    image = fields.Binary(string='Doctor Image')

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = 'New Doctor'
        if vals.get('doctor_reference', _('New')) == _('New'):
            vals['doctor_reference'] = self.env['ir.sequence'].next_by_code('hospital.doctor') or _('New')
        res = super(HospitalDoctor, self).create(vals)
        return res

class HospitalNurse(models.Model):
    _name = 'hospital.nurse'
    _description = 'Hospital Nurse'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'nurse_name'

    nurse_reference = fields.Char(string="Nurse Reference", 
									required=True, copy=False, readonly=True,
									default=lambda self: _('New'))
    nurse_name = fields.Char(string='Name', required=True, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    gender = fields.Selection(string='Gender', selection=[
        ('male', 'Male'), 
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='male', tracking=True)
    note = fields.Text(string='Description')
    image = fields.Binary(string='Nurse Image')

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = 'New Nurse'
        if vals.get('nurse_reference', _('New')) == _('New'):
            vals['nurse_reference'] = self.env['ir.sequence'].next_by_code('hospital.nurse') or _('New')
        res = super(HospitalNurse, self).create(vals)
        return res