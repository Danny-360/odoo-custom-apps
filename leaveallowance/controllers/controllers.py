# -*- coding: utf-8 -*-
# from odoo import http


# class Custom/leaveAllowance(http.Controller):
#     @http.route('/custom/leave_allowance/custom/leave_allowance', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom/leave_allowance/custom/leave_allowance/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom/leave_allowance.listing', {
#             'root': '/custom/leave_allowance/custom/leave_allowance',
#             'objects': http.request.env['custom/leave_allowance.custom/leave_allowance'].search([]),
#         })

#     @http.route('/custom/leave_allowance/custom/leave_allowance/objects/<model("custom/leave_allowance.custom/leave_allowance"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom/leave_allowance.object', {
#             'object': obj
#         })
