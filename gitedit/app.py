# -*- coding: utf-8 -*-
"""
Site to access klein
"""
import logging
import json

from klein import Klein
import pygit2

from gitedit.repo import RemoteRepo

DEV_LOGGER = logging.getLogger(__name__)


class GitEditJSONEncoder(json.JSONEncoder):
    @staticmethod
    def stringify_const(const, options, module):
        return [attr_name for attr_name in options if getattr(module, attr_name) == const][0]

    def default(self, obj):
        if isinstance(obj, pygit2.Commit):
            return {key: getattr(obj, key) for key in
                    ("id",
                     "type",
                     "author",
                     "committer",
                     "message",
                     "message_encoding",
                     "raw_message",
                     "tree_id",
                     "parent_ids",
                     "commit_time",
                     "commit_time_offset")}
        elif isinstance(obj, pygit2.Signature):
            return {key: getattr(obj, key) for key in
                    ("name",
                     "raw_name",
                     "email",
                     "raw_email",
                     "time",
                     "offset")}
        elif isinstance(obj, pygit2.Reference):
            output = {key: getattr(obj, key) for key in
                      ("name",
                       "shorthand",
                       "target",
                       "type"
                       )}

            if obj.resolve() != obj:
                output["resolved"] = obj.resolve()
            output["type_string"] = self.stringify_const(obj.type,
                                                         ("GIT_REF_OID", "GIT_REF_SYMBOLIC"),
                                                         pygit2)
            return output
        elif isinstance(obj, pygit2.TreeEntry):
            output = {key: getattr(obj, key) for key in
                      ("name",
                       "id",
                       "filemode")}
            output["filemode_string"] = self.stringify_const(
                obj.filemode,
                ("GIT_FILEMODE_BLOB",
                 "GIT_FILEMODE_BLOB_EXECUTABLE",
                 "GIT_FILEMODE_TREE",
                 "GIT_FILEMODE_LINK",
                 "GIT_FILEMODE_COMMIT"),
                pygit2)
            return output
        elif isinstance(obj, pygit2.Oid):
            return unicode(obj)
        elif isinstance(obj, pygit2.Blob):
            output = {key: getattr(obj, key) for key in
                      ("id",
                       "type",
                       "data",
                       "size",
                       "is_binary",
                       )}
            output["type_string"] = self.stringify_const(
                obj.type,
                ("GIT_OBJ_COMMIT", "GIT_OBJ_TREE", "GIT_OBJ_BLOB", "GIT_OBJ_TAG"),
                pygit2)
            return output

        return super(GitEditJSONEncoder, self).default(obj)


class GitEditApp(object):
    app = Klein()

    def __init__(self, clone_url, reference, domain):
        self._clone_url = clone_url
        self._domain = domain

        self._remote = RemoteRepo(self._clone_url)

        self._gitedit_user = "gitedit"
        self._gitedit_name = "GitEdit"
        self._default_reference = reference

        self._committer = pygit2.Signature(self._gitedit_name,
                                           "%s@%s" % (self._gitedit_user, self._domain))

        self._json_encoder = GitEditJSONEncoder(indent=2)

    def _get_commit(self, reference_id):
        reference = self._remote.repo.lookup_reference(reference_id)
        commit = reference.get_object()
        assert commit.type == pygit2.GIT_OBJ_COMMIT

        tree_builder = self._remote.repo.TreeBuilder(commit.tree)

        return (reference, commit, tree_builder)

    @app.route('/tree/<path:tree_path>', methods=["GET"])
    def read(self, request, tree_path):
        reference, commit, tree_builder = self._get_commit(self._default_reference)

        try:
            tree_entry = tree_builder.get(tree_path)
        except KeyError:
            request.setResponseCode(404)
            return "No file found"

        blob = self._remote.repo.get(tree_entry.id)

        return self._json_encoder.encode({"reference": reference,
                                          "commit": commit,
                                          "tree_entry": tree_entry,
                                          "blob": blob
                                          })
