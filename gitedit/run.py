# -*- coding: utf-8 -*-
"""
Run app
"""
import logging

from twisted.web import server
from twisted.internet import reactor
from twisted.python import log
from twisted.cred.portal import Portal
from twisted.web.guard import HTTPAuthSessionWrapper, BasicCredentialFactory
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse


from gitedit.site import GitEditApp
from gitedit.authentication import GitEditRealm

DEV_LOGGER = logging.getLogger(__name__)


def run():
    domain = "domain.com"
    observer = log.PythonLoggingObserver()
    observer.start()

    logging.basicConfig(level=logging.DEBUG)

    import sys
    edit_app = GitEditApp(sys.argv[1], domain)
    realm = GitEditRealm(edit_app)

    test_pw_db = InMemoryUsernamePasswordDatabaseDontUse(test="testpw")
    credential_factory = BasicCredentialFactory(domain)

    portal = Portal(realm, [test_pw_db])

    resource = HTTPAuthSessionWrapper(portal, [credential_factory])
    site = server.Site(resource)

    reactor.listenTCP(8080, site)
    reactor.run()


if __name__ == "__main__":
    run()
