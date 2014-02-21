# -*- coding: utf-8 -*-
"""
Site to access klein
"""
import logging

from klein import Klein
from gitedit.git_editor import GitEditor
import pygit2

DEV_LOGGER = logging.getLogger(__name__)


class GitEditApp(object):
    app = Klein()

    def __init__(self, site, domain):
        self._site = site
        self._domain = domain
        self._gitedit_user = "gitedit"
        self._gitedit_name = "GitEdit"
        self._editor = GitEditor(self._site)
        self._default_reference = "refs/heads/master"
        self._committer = pygit2.Signature(self._gitedit_name,
                                           "%s@%s" % (self._gitedit_user, self._domain))

    @app.route('/<string:path>', methods=["GET"])
    def read(self, request, path):
        try:
            return self._editor.get_tree_editor(self._default_reference).read_file(path)
        except KeyError:
            request.setResponseCode(404)
            return "No file found"

    @app.route('/<string:path>', methods=["PUT"])
    def write(self, request, path):
        tree_editor = self._editor.get_tree_editor(self._default_reference)
        try:
            tree_editor.write_file(path, request.content.read())
        except KeyError:
            request.setResponseCode(404)
            return "No file found"
        user = pygit2.Signature(request.getUser(), "%s@%s" % (request.getUser(),
                                                              self._domain))
        tree_editor.commit(self._default_reference, user, self._committer, "Web commit")
        self._editor.push(self._default_reference)
