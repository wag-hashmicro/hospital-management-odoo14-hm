from odoo import api, fields, models, _, modules
import base64

def get_default_doctor_img():
		with open(modules.get_module_resource('wag_hospital', 'static/img', 'doctor.png'), 'rb') as f:
			return base64.b64encode(f.read())

def get_default_nurse_img():
		with open(modules.get_module_resource('wag_hospital', 'static/img', 'nurse.png'), 'rb') as f:
			return base64.b64encode(f.read())

def get_default_cleaning_service_img():
		with open(modules.get_module_resource('wag_hospital', 'static/img', 'cleaning_service.png'), 'rb') as f:
			return base64.b64encode(f.read())

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
    image = fields.Binary(string='Doctor Image', default=get_default_doctor_img())

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
    image = fields.Binary(string='Nurse Image', default=get_default_nurse_img())

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = 'New Nurse'
        if vals.get('nurse_reference', _('New')) == _('New'):
            vals['nurse_reference'] = self.env['ir.sequence'].next_by_code('hospital.nurse') or _('New')
        res = super(HospitalNurse, self).create(vals)
        return res

class HospitalCleaningService(models.Model):
    _name = "hospital.cleaning.service"
    _description = 'Hospital Cleaning Service'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    cleaning_service_reference = fields.Char(string="Cleaning Service Reference", 
									required=True, copy=False, readonly=True,
									default=lambda self: _('New'))
    name = fields.Char(string='Name', required=True, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    gender = fields.Selection(string='Gender', selection=[
        ('male', 'Male'), 
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='female', tracking=True)
    note = fields.Text(string='Description')
    image = fields.Binary(string='Cleaning Service Image', default=get_default_cleaning_service_img())

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = 'New Cleaning Service'
        if vals.get('cleaning_service_reference', _('New')) == _('New'):
            vals['cleaning_service_reference'] = self.env['ir.sequence'].next_by_code('hospital.cleaning.service') or _('New')
        res = super(HospitalCleaningService, self).create(vals)
        return res
    
