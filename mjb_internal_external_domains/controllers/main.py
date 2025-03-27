# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tools import consteq
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import logging
from odoo.addons.portal.controllers.web import Home
from odoo import http, _
from odoo.http import request
from odoo import SUPERUSER_ID
_logger = logging.getLogger(__name__)


def rakDebug(mArr):
    debug = True
    if debug:
        for m in mArr:
            _logger.info('[MAJORBIRD] ' + str(m))


def checkAccess(_url, _user, _env, pageType='portal'):
    externalDomain = _env['ir.config_parameter'].sudo().get_param('mjb_portal_share.external_domain')
    internalDomain = _env['ir.config_parameter'].sudo().get_param('mjb_portal_share.internal_domain')
    
    # if config not set, do not block
    if not externalDomain or not internalDomain:
        accessGranted = True
        rakDebug([
            pageType,
            "accessGranted as there is no external or internal domain set",
            accessGranted
        ])
        return True

    # externalDomain = "8070-mjbcustomer-gitpodrakst-r63bah8lzep.ws-us54.gitpod.io"
    # internalDomain = "8069-mjbcustomer-gitpodrakst-r63bah8lzep.ws-us54.gitpod.io"

    isInternalDomain = internalDomain in _url
    isExternalDomain = externalDomain in _url

    # user_isPublic = request.env.user._is_public()
    user_isPublic = _user._is_public()
    user_groupHasInternal = _user.sudo().has_group('base.group_user')
    user_groupHasPortal = _user.sudo().has_group('base.group_portal')
    user_groupHasPublic = _user.sudo().has_group('base.group_public')

    isPublicUserOnExternalDomain = isExternalDomain and user_isPublic
    isPortalUserOnExternalDomain = isExternalDomain and user_groupHasPortal
    isExternalUserOnExternalDomain = isPublicUserOnExternalDomain or isPortalUserOnExternalDomain

    isPublicUserOnInternalDomain = isInternalDomain and user_isPublic
    isPortalUserOnInternalDomain = isInternalDomain and user_groupHasPortal
    isExternalUserOnInternalDomain = isPublicUserOnInternalDomain or isPortalUserOnInternalDomain

    isInternalUserOnInternalDomain = isInternalDomain and user_groupHasInternal
    isInternalUserOnExternalDomain = isExternalDomain and user_groupHasInternal

    accessGranted = False

    if pageType == 'login':
        if isExternalDomain:
            accessGranted = isPublicUserOnExternalDomain or isPortalUserOnExternalDomain
        
        if isInternalDomain:
            accessGranted = isInternalUserOnInternalDomain or isPublicUserOnInternalDomain
    
    if pageType == 'portal':
        if isExternalDomain:
            accessGranted = isExternalUserOnExternalDomain
        
        if isInternalDomain:
            accessGranted = isInternalUserOnInternalDomain or isPublicUserOnInternalDomain
    
    rakDebug([
        pageType,
        "accessGranted",
        accessGranted
    ])
    return accessGranted


class Website(Home):

    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        values = request.params.copy()
        
        if request.httprequest.method == 'GET':
            accessGranted = checkAccess(
                request.httprequest.url_root,
                request.env.user,
                request.env,
                'login'
            )
            if not accessGranted:
                values['error'] = _("Forbidden")
                return request.render('web.login', values)

        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        # try:
        #     values['databases'] = http.db_list()
        # except odoo.exceptions.AccessDenied:
        values['databases'] = None
        
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            ip_address = request.httprequest.environ['REMOTE_ADDR']

            if request.params['login']:
                user_rec = request.env['res.users'].sudo().search( [('login', '=', request.params['login'])])

                accessGranted = False
                if len(user_rec) > 0:
                    accessGranted = checkAccess(
                        request.httprequest.url_root,
                        user_rec[0],
                        request.env,
                        'portal'
                    )

                if accessGranted:
                    try:
                        credential = {'login': request.params['login'], 'password': request.params['password'], 'type': 'password'}
                        uid = request.session.authenticate(
                            request.db,
                            credential
                        )
                        request.params['login_success'] = True
                        return request.redirect(self._login_redirect(uid, redirect=redirect))
                    except:
                        # odoo.exceptions.AccessDenied as e
                        request.update_env(user=old_uid)
                        # if e.args == odoo.exceptions.AccessDenied().args:
                        values['error'] = _("Wrong login/password")
                else:
                    values['error'] = _("Forbidden")
                
        return request.render('web.login', values)


class CustomerPortal(CustomerPortal):

    def _document_check_access(self, model_name, document_id, access_token=None):
        url = request.httprequest.url_root
        accessGranted = checkAccess(
            url,
            request.env.user,
            request.env,
            'portal'
        )

        if not accessGranted:
            raise MissingError(_("Forbidden"))
            # values = request.params.copy()
            # values['error'] = _("Forbidden")
            # return request.render('web.login', values)
        
        document = request.env[model_name].browse([document_id])
        document_sudo = document.with_user(SUPERUSER_ID).exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if not access_token or not document_sudo.access_token or not consteq(document_sudo.access_token, access_token):
                raise
        return document_sudo
