from odoo import api, models, fields, _
from datetime import datetime

class CreateAppointmentWizard(models.TransientModel):
	_name = "create.appointment.wizard"
	_description = "Create Appoinment Wizard"
	
	date_appointment = fields.Date(string="Date", default=datetime.today(), readonly=True)
	order_reference = fields.Char(string="Order Reference", 
									required=True, copy=False, readonly=True,
									default=lambda self: _('New'))
	patient_id = fields.Many2one('hospital.patient', string='Patient')
	doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
	age = fields.Integer(string='Age', related='patient_id.age',tracking=True)
	responsible_id = fields.Many2one('res.partner', 
									string='Responsible')
	date_checkup = fields.Datetime(string="Check Up Time")
	gender = fields.Selection([('male', 'Male'), 
								('female', 'Female'), 
								('other', 'Other'),], 
								required=True, 
								default='male', 
								related='patient_id.gender', 
								tracking=True)
	note = fields.Text(string='Description')
	
	

	def action_create_appointment(self):
		print('Button Clicked')
		vals = {
			'patient_id' : self.patient_id.id,
			'doctor_id' : self.doctor_id.id,
			'date_checkup' : self.date_checkup,
			'date_appointment' : self.date_appointment,
			'responsible_id' : self.responsible_id.id,
			'note' : self.note,
		}
		appointment_rec = self.env['hospital.appointment'].create(vals) 
		print("patient_id", appointment_rec)
		return {
			"name": ("Appointment"),
			"type": "ir.actions.act_window",
			"view_mode": "form",
			"res_model": "hospital.appointment",
			"res_id": appointment_rec.id,
		}
		
	def action_view_appointment(self):
		#Method-1
		action = self.env.ref('om_hospital.action_appointment_patient').read()[0]
		return action
		
		#Method-2
		#action = self.env['ir.actions.actions']._for_xml_id('om_hospital.action_appointment_patient')
		#action['domain'] = [('patient_id', '=', self.patient_id.id)]
		#return action
		
		