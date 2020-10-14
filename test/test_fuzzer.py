from flask import Flask
from openapi3_fuzzer import FuzzIt, do_fuzzing
from flask_testing import TestCase


class TestFuzzer(TestCase):

    def create_app(self):
        return Flask("test_app")

    def test_generic_positive(self):
        assert 0xDEADBEEF

    def test_do_fuzzing(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer '
        }
        assert do_fuzzing(self, headers, "test/openapi.yaml") == 1

    def test_FuzzIt_no_errors(self):
        assert FuzzIt("test/openapi.yaml", '', self)
