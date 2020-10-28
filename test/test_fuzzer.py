from flask import Flask
from openapi3_fuzzer import FuzzIt, do_fuzzing
from prance import ValidationError
from flask_testing import TestCase


class OtherTest(TestCase):
    def create_app(self):
        pass


class TestFuzzer(TestCase):

    def create_app(self):
        return Flask("test_app")

    def test_generic_positive(self):
        assert 0xDEADBEEF

    def test_do_fuzzing(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer',
        }
        assert do_fuzzing(self, headers, "test/openapi.yaml") == 2

    def test_FuzzIt_no_errors(self):
        assert FuzzIt("test/openapi.yaml", 'test', self)

    def test_no_test_client(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer',
        }
        new_test_case = OtherTest()
        self.assertRaises(AttributeError, do_fuzzing, new_test_case, headers, "test/openapi.yaml")

    def test_invalid_spec(self):
        self.assertRaises(ValidationError, FuzzIt, "test/invalid-openapi.yaml", 'test', self)

    def test_no_paths_spec(self):
        self.assertRaises(ValidationError, FuzzIt, "test/no-paths-openapi.yaml", 'test', self)
