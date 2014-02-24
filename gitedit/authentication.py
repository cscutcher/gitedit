# -*- coding: utf-8 -*-
"""
Authenticate users for gitedit
"""
import logging

from zope.interface import implements
from twisted.web.resource import IResource
from twisted.cred.portal import IRealm

from gitedit.resource import GitResource

DEV_LOGGER = logging.getLogger(__name__)


class GitEditRealm(object):
    implements(IRealm)

    def __init__(self, default_resource):
        self._resource = default_resource

    def requestAvatar(self, avatar_id, mind, *interfaces):
        return (IResource, self._resource, lambda: None)
