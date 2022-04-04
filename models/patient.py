from odoo import api, fields, models, modules
import base64

def get_default_patient_img():
		with open(modules.get_module_resource('wag_hospital', 'static/img', 'patient.png'), 'rb') as f:
			return base64.b64encode(f.read())

class HospitalPatient(models.Model):
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_name = "hospital.patient"
	_description = "Hospital Patient"
	
	reference = fields.Char(string="Patient Reference", required=True, copy=False, readonly=True, 
							default=lambda self: ('New'))
	name = fields.Char(string='Name', required=True, tracking=True)
	age = fields.Integer(string='Age', tracking=True)
	gender = fields.Selection([
								('male', 'Male'), 
								('female', 'Female'), 
								('other', 'Other'),], 
								required=True, 
								default='male', 
								tracking=True)
	note = fields.Text(string='Description')
	state =  fields.Selection([('register', 'Register'), ('checkup', 'Check Up'), ('appointment', 'Appointment'), ('checkin', 'Check In'), 
								('done', 'Done'), ('cancel', 'Canceled'), ('checkout', 'Check Out')], 
								tracking=True, 
								default='register', 
								string='Status')
	responsible_id = fields.Many2one('res.partner', string='Responsible')
	appointment_count = fields.Integer(string='Total Appointment', compute='_compute_appointment_count')
	image = fields.Binary(string='Patient Image', default=get_default_patient_img())

	def _compute_appointment_count(self):
		for rec in self:
			appointment_count = self.env['hospital.appointment'].search_count([('patient_id', '=', rec.id)])
			rec.appointment_count = appointment_count
	
	@api.model
	def create(self, vals):
		if not vals.get('note'):
			vals['note'] = "New Patient"
		if vals.get('reference', ('New')) == ('New'):
			vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.patient') or ('New')
		res = super(HospitalPatient, self).create(vals)
		return res
		
	@api.model
	def default_get(self, fields):
		res = super(HospitalPatient, self).default_get(fields)
		res['note'] = 'Default note value'
		return res
	
	def action_checkin(self):
		self.state = 'checkin'

	def action_checkout(self):
		self.state = 'checkout'

	def action_register(self):
		self.state = 'register'

	def action_appointment(self):
		self.state = 'appointment'
		
	def action_checkup(self):
		self.state = 'checkup'
		
	def action_done(self):
		self.state = 'done'
		
	def action_cancel(self):
		self.state = 'cancel'