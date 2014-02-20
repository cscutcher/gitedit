# -*- coding: utf-8 -*-
"""
UnitTests
"""
import logging
import unittest

import pygit2

from gitedit.git_editor import GitEditor

DEV_LOGGER = logging.getLogger(__name__)


class TestGitEditor(unittest.TestCase):
    def test_edit(self):
        TEST_CONTENTS = "hello world"
        TEST_BRANCH = "refs/heads/master"
        TEST_FILE = "README.md"
        editor = GitEditor("GITURL")
        tree_editor = editor.get_tree_editor(TEST_BRANCH)
        tree_editor.write_file(TEST_FILE, TEST_CONTENTS)
        me = pygit2.Signature("Unknown user", "unknown@server")
        tree_editor.commit(TEST_BRANCH, me, me, "Test commit")

        tree_editor = editor.get_tree_editor(TEST_BRANCH)
        contents = tree_editor.read_file(TEST_FILE)
        self.assertEqual(contents, TEST_CONTENTS)

        editor.push(TEST_BRANCH)


all_suite = unittest.TestLoader().loadTestsFromTestCase(TestGitEditor)
