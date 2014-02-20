# -*- coding: utf-8 -*-
"""
Site to access klein
"""
import logging

from klein import Klein
from gitedit.git_editor import GitEditor
import pygit2

DEV_LOGGER = logging.getLogger(__name__)


class GitEditServer(object):
    app = Klein()

    def __init__(self):
        self._editor = GitEditor("/home/cscutcher/git/gitedit/test-git.bare/")
        self._default_reference = "refs/heads/master"
        self._committer = pygit2.Signature("GitEdit", "gitedit@server")

    @app.route('/<string:path>', methods=["GET"])
    def read(self, request, path):
        return self._editor.get_tree_editor(self._default_reference).read_file(path)

    @app.route('/<string:path>', methods=["PUT"])
    def write(self, request, path):
        tree_editor = self._editor.get_tree_editor(self._default_reference)
        tree_editor.write_file(path, request.content.read())
        me = pygit2.Signature("Unknown user", "unknown@server")
        tree_editor.commit(self._default_reference, me, self._committer, "Web commit")
        self._editor.push(self._default_reference)

if __name__ == "__main__":
    import sys
    site = GitEditServer(sys.argv[1])
    site.app.run("localhost", 8080)
