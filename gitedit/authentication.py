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

    def __init__(self, repo, reference):
        self._repo = repo
        self._reference = reference

    def requestAvatar(self, avatar_id, mind, *interfaces):
        reference = self._repo.get_repo().lookup_reference(self._reference)
        commit = reference.get_object()
        resource = GitResource(avatar_id, self._repo, commit)
        return (IResource, resource, lambda: None)
