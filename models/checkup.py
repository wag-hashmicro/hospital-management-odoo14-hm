from datetime import datetime
from odoo import api, fields, models, _

class HospitalCheckup(models.Model):
    _name = 'hospital.checkup'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Checkup'
    _rec_name = "checkup_reference"

    service_checkup_ids = fields.One2many(
        comodel_name='hospital.service.checkup.detail', 
        inverse_name='checkup_id', 
        string='Checkup Service')

    checkup_reference = fields.Char(string="Check Up Reference", required=True, copy=False, readonly=True, 
                                    default=lambda self: _('New'))
    date_checkup = fields.Datetime(string="Date", default=datetime.now(), readonly=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    responsible_id = fields.Many2one('res.partner', string='Responsible', related='patient_id.responsible_id')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    diagnoses = fields.Text(string='Diagnoses')
    recipe = fields.Char(string='Recipe')
    inpatient = fields.Boolean(string='Inpatient')
    note = fields.Text(string='Note')
    state =  fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                                ('done', 'Done'), ('cancel', 'Canceled')], 
                                tracking=True,default='draft', string='Status')

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

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = "New Checkup"
        if vals.get('checkup_reference', _('New')) == _('New'):
            vals['checkup_reference'] = self.env['ir.sequence'].next_by_code('hospital.checkup') or _('New')
        res = super(HospitalCheckup, self).create(vals)
        if res.checkup_reference:
            self.env['hospital.patient'].search([('id','=',res.patient_id.id)]).write({'state':'checkup'})
        return res
    
    def unlink(self):
        for record in self:
            self.env['hospital.patient'].search([('id','=',record.patient_id.id)]).write({'state':'done'})
        record = super(HospitalCheckup, self).unlink()

    def action_show_create_checkin(self):
        return {
            "name": ("Create Check In"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "create.checkin.wizard",
            "target": "new",
            "views": [[self.env.ref('om_hospital.view_create_checkin_form').id, "form"]],
        }
    
class HospitalServiceCheckupDetail(models.Model):
    _name = 'hospital.service.checkup.detail'
    _description = 'New Description'

    name = fields.Char(string='Name')

    service_checkup_id = fields.Many2one('hospital.service.checkup', string='Service Checkup')
    checkup_id = fields.Many2one(comodel_name='hospital.checkup', string='Checkup')

    price = fields.Integer(string='Price', related='service_checkup_id.price')

