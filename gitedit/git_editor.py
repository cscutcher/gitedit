# -*- coding: utf-8 -*-
"""
GitEditor class
"""
import logging
import tempfile
import shutil

import pygit2

DEV_LOGGER = logging.getLogger(__name__)


class TreeEditor(object):
    def __init__(self, repo, parent_commit):
        self._repo = repo
        self._parent_commit = parent_commit
        self._tree = self._repo.TreeBuilder(parent_commit.tree)

    def read_file(self, path):
        tree_entry = self._tree.get(path)
        if tree_entry is None:
            raise KeyError
        blob_id = tree_entry.id
        blob = self._repo.get(blob_id)
        return blob.data

    def write_file(self, path, data):
        blob_id = self._repo.create_blob(data)
        self._tree.insert(path, blob_id, pygit2.GIT_FILEMODE_BLOB)

    def commit(self, reference, author, committer, message):
        tree_id = self._tree.write()
        commit_id = self._repo.create_commit(reference,
                                             author,
                                             committer,
                                             message,
                                             tree_id,
                                             [self._parent_commit.id])
        return commit_id


class GitEditor(object):
    def __init__(self, clone_url):
        super(GitEditor, self).__init__()
        self._clone_url = clone_url
        self._reference = 'refs/remotes/origin/master'

        self._git_mirror_dir = None
        self._git_mirror = None

        self._init_git_mirror()

    def _init_git_mirror(self):
        if self._git_mirror is None:
            self._git_mirror_dir = tempfile.mkdtemp(suffix="git")
            self._git_mirror = pygit2.clone_repository(self._clone_url,
                                                       self._git_mirror_dir,
                                                       bare=True)

    def _remove_git_mirror(self):
        if self._git_mirror is not None:
            shutil.rmtree(self._git_mirror_dir)
            self._git_mirror_dir = None
            self._git_mirror = None

    def fetch(self):
        for remote in self._git_mirror.remotes:
            remote.fetch()

    def push(self, reference_id):
        self._git_mirror.remotes[0].push(reference_id)

    def get_tree_editor(self, reference_id):
        self.fetch()
        reference = self._git_mirror.lookup_reference(reference_id)
        commit = reference.get_object()
        return TreeEditor(self._git_mirror, commit)

    def __del__(self):
        self._remove_git_mirror()
