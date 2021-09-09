# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

class ChequeRechazado(models.Model):
    _name = 'cheque.rechazado'
    _rec_name = 'cliente_id'

    cliente_id = fields.Many2one('res.partner','Cliente', required = True)
    banco_id = fields.Many2one('account.journal','Banco', required = True)
    cuenta_cobrar_id = fields.Many2one('account.account','Cuenta a cobrar')
    numero_deposito = fields.Char('Número de depósito')
    numero_cheque = fields.Char('Número de cheque')
    motivo_rechazo = fields.Char('Motivo rechazo')
    fecha = fields.Date('Fecha')
    monto = fields.Float('Monto')
    estado = fields.Selection([
        ('nuevo', 'Nuevo'),
        ('cobrar','Por cobrar'),
        ('recuperado','Recuperado'),
    ], string='Estado', help='Estado',readonly=True, default='nuevo')
    asiento_ids = fields.Many2many('account.move', string='Asientos')

    def cancelar(self):
        for documento in self:
            if documento.asiento_ids:
                for asiento in documento.asiento_ids:
                    asiento.button_draft()
                    asiento.button_cancel()
            documento.estado = 'nuevo'

    def cobrar(self):
        for documento in self:
            if documento.cuenta_cobrar_id and documento.banco_id.default_account_id:
                asiento = {'move_type': 'entry','ref': documento.numero_deposito,'date': documento.fecha,'journal_id': documento.banco_id.id,}
                asiento_id = self.env['account.move'].create(asiento)
                if asiento_id:
                    apuntes = []
                    apuntes.append((0,0,{'move_id': asiento_id.id,
                        'account_id': documento.cuenta_cobrar_id.id,'name': documento.numero_cheque,
                        'partner_id': documento.cliente_id.id,'debit': documento.monto,'credit':0}))
                    apuntes.append((0,0,{'move_id': asiento_id.id,
                        'account_id': documento.banco_id.default_account_id.id,'name': documento.numero_cheque,
                        'partner_id': documento.cliente_id.id,'debit': 0,'credit':documento.monto}))
                    asiento_id.write({'line_ids' : apuntes})
                    asiento_id.action_post()
                    documento.write({'asiento_ids': [(4, asiento_id.id)] })
                    documento.estado = 'cobrar'
        return True

    def recuperar(self):
        for documento in self:
            if documento.cuenta_cobrar_id and documento.banco_id.default_account_id:
                asiento = {'move_type': 'entry','ref': documento.numero_deposito,'date': documento.fecha,'journal_id': documento.banco_id.id,}
                asiento_id = self.env['account.move'].create(asiento)
                if asiento_id:
                    apuntes = []
                    apuntes.append((0,0,{'move_id': asiento_id.id,
                        'account_id': documento.cuenta_cobrar_id.id,'name': documento.numero_cheque,
                        'partner_id': documento.cliente_id.id,'debit': 0,'credit':documento.monto}))
                    apuntes.append((0,0,{'move_id': asiento_id.id,
                        'account_id': documento.banco_id.default_account_id.id,'name': documento.numero_cheque,
                        'partner_id': documento.cliente_id.id,'debit': documento.monto,'credit':0}))
                    asiento_id.write({'line_ids' : apuntes})
                    asiento_id.action_post()
                    documento.write({'asiento_ids': [(4, asiento_id.id)] })
                    documento.estado = 'recuperado'
