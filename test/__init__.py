import unittest
import connexion
from flask_testing import TestCase


def load_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('test', pattern='test_*.py')
    return test_suite


class BasePositiveTestCase(TestCase):

    def create_app(self):
        app = connexion.App(__name__, specification_dir='app/openapi/')
        app.add_api('openapi.yaml', pythonic_params=True)
        return app.app
