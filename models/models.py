# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import models, fields, api, tools
_logger = logging.getLogger(__name__)

class hr_appraisal(models.Model):
    _name = 'hr.hr_appraisal'

    employee = fields.Many2one('hr.employee', string='Employee', ondelete='cascade', help="Select the employee for Appraisal Process.", required = True)
    final_appraisal = fields.Integer(string= 'Appraisal amount')
    target_ids = item_ids = fields.One2many('hr.hr_appraisal.targets','appraisal_id')
    company_evaluation_id = fields.One2many('hr.hr_appraisal.targets','appraisal_id')

    @api.model
    def create(self,values):
        record = super(hr_appraisal, self).create(values)
        manager_id = self.env['hr.employee'].browse(values.get('employee')).department_id.manager_id.id
        if not manager_id:
            manager_id = 1
        self.env['hr.hr_appraisal.company_evaluation'].create({
            'appraisal_id': record.id,
            'manager_id': manager_id
        })
        return record
    # @api.depends('value')
    # def _value_pc(self):
    #     self.value2 = float(self.value) / 100  

class hr_appraisal_targets(models.Model):
    _name = 'hr.hr_appraisal.targets'

    appraisal_id = fields.Many2one('hr.hr_appraisal')
    target = fields.Char(string = 'Target Name')
    completed = fields.Boolean("Project completed", default= False)
    performance_rating = fields.Integer(string = 'Performance Rating', help= 'Rate from 1-5 on basis of performance in the project. ')
    quality_rating = fields.Integer(string = 'Quality Rating', help = 'Rate from 1-5 on basis of quality of work done in the project.')
    deadline_meeting_rating = fields.Integer(string = "Deadline meeting rating", help = 'Rate from 1-5 on whether the deadline of project was met on time.')
    comments = fields.Text('Comments')

class hr_appraisal_company_evaluation(models.Model):
    _name = 'hr.hr_appraisal.company_evaluation'
    
    appraisal_id = fields.Many2one('hr.hr_appraisal')
    manager_id = fields.Integer()
    attendance = fields.Integer(string = "Attendance")
    communication_skills_rating = fields.Integer(string = "Communication Skills Rating", help = 'Rate employee from 1-5 on basis of communication skills of employee')
    quality_rating = fields.Integer(string = "Work Quality Rating", help = 'Rate employee from 1-5 on basis of work quality of employee')
    performance_rating = fields.Integer(string = "Performance Rating", help = 'Rate employee from 1-5 on basis of performance of employee')
    skill_set_rating = fields.Integer(string = "Skill Sets Rating", help = 'Rate employee from 1-5 on basis of skill sets of employee')
    deadlines_meeting_rating = fields.Integer(string = "Deadlines meeting rating", help = 'Rate employee from 1-5 on whether employee meets project deadlines on time')
    employee_overall_rating = fields.Integer(string = 'Employee rating')
    comments = fields.Text('Comments')

class hr_appraisal_scheduler(models.Model):
    _name = 'hr.hr_appraisal.scheduler'

    name = fields.Char(string="Name of the appraisal", required=True)
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    schedule_on = fields.Boolean(string="Active", default="False")
    completed  = fields.Boolean(string="Completed", default="False")

    @api.constrains('start_date', 'end_date')
    def _check_schedule(self):
        now = fields.Datetime.now()
        if(self.start_date <= now ):
            raise ValidationError('Start time must be upcoming time from right now')
        elif self.start_date >= self.end_date:
            _logger.warning('checking violation1')
            raise ValidationError('End Date cannot be set before or same as Start Date.')
        for appraisal in self.env['hr.hr_appraisal.scheduler'].search([]):
            _logger.warning('checking violation1.2')
            if (self.start_date >= appraisal.start_date and self.start_date <= appraisal.end_date) or (self.end_date <= appraisal.end_date and self.end_date >= appraisal.start_date ):
                _logger.warning('checking violation2')
                raise ValidationError('This time range cannot be selected as it is clashing with other appraisal process: %r:' % appraisal.name)
            elif self.start_date <= appraisal.start_date and self.end_date >= appraisal.end_date:
                _logger.warning('checking violation3')
                raise ValidationError('This time range cannot be selected as it is clashing with other appraisal process: %r:' % appraisal.name)


    # @api.one
    # def execute(self):
    #     now = fields.Datetime.now()
    #     _logger.warning('Content11111: %r',now)

    #     if self.end_date <= now:
    #         _logger.info('Content11111: %r',now)
    #         self.write({'completed': True})
    #         self.write({'active': False})
    #     elif self.start_date <= now and self.end_date >= now:
    #         _logger.info('Content22222: %r',now)
    #         if self.schedule_on != True:
    #             self.write({'schedule_on': True})
    #     return True

    @api.model
    def _start_appraisal_process(self, autocommit=False):    
        _logger.warning('Conten33333333333333333')
        for scheduler in self.env['hr.hr_appraisal.scheduler'].search([]):
            # scheduler.execute()
            now = fields.Datetime.now()
            _logger.warning('Content11111: %r',scheduler.name)
            if scheduler.end_date <= now and scheduler.completed != True:
                _logger.info('Content21111: %r',now)
                scheduler.write({'completed': True})
                scheduler.write({'schedule_on': False})
            elif scheduler.start_date <= now and scheduler.end_date >= now and scheduler.schedule_on != True and scheduler.completed != True:
                _logger.info('Content22222: %r',now)
                scheduler.write({'schedule_on': True})                        
        if autocommit:
            self.env.cr.commit()
        return True


        
        
