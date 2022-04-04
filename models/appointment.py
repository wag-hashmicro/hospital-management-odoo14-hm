from odoo import api, fields, models, _
from datetime import datetime

class HospitalAppointment(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = "hospital.appointment"
    _description = "Hospital Appointment"
    _rec_name = 'order_reference'
    
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    patient_image = fields.Binary(string='Patient Image', related='patient_id.image')
    responsible_id = fields.Many2one('res.partner', string='Responsible')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)
    age = fields.Integer(string='Age', related='patient_id.age',tracking=True)
    order_reference = fields.Char(string="Order Reference", 
                                    required=True, copy=False, readonly=True,
                                    default=lambda self: _('New'))
    note = fields.Text(string='Description')
    state =  fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                                ('done', 'Done'), ('cancel', 'Canceled')], 
                                tracking=True,default='draft', string='Status')
    gender = fields.Selection([('male', 'Male'), 
                                ('female', 'Female'), 
                                ('other', 'Other'),], 
                                required=True, 
                                default='male', 
                                related='patient_id.gender', 
                                tracking=True)
    date_appointment = fields.Date(string="Date", default=fields.Date.today(), readonly=True)
    date_checkup = fields.Datetime(string="Check Up Time") 
    
    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = "New Appointment"
        if vals.get('order_reference', ('New')) == ('New'):
            vals['order_reference'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or ('New')
        res = super(HospitalAppointment, self).create(vals)
        if res.order_reference:
            self.env['hospital.patient'].search([('id','=',res.patient_id.id)]).write({'state':'appointment'})
        return res

    def unlink(self):
        for record in self:
            self.env['hospital.patient'].search([('id','=',record.patient_id.id)]).write({'state':'done'})
        record = super(HospitalAppointment, self).unlink()
    
    def action_confirm(self):
        self.state = 'confirm'
        
    def action_draft(self):
        self.state = 'draft'
        
    def action_done(self):
        self.state = 'done'
        self.env['hospital.patient'].search([('id','=',self.patient_id.id)]).write({'state':'done'})
        
    def action_cancel(self):
        self.state = 'cancel'
        self.env['hospital.patient'].search([('id','=',self.patient_id.id)]).write({'state':'cancel'})
        
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            if self.patient_id.responsible_id:
                self.responsible_id = self.patient_id.responsible_id
            else:
                self.responsible_id = ''
            if self.patient_id.note:
                self.note = self.patient_id.note
        else:
            self.responsible_id = ''
            self.note = ''