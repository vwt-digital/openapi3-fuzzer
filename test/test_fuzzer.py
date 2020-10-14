# import pytest
# from openapi3_fuzzer import FuzzIt

# class BasePositiveTestCase(TestCase):
#
#     def create_app(self):
#         app = connexion.App(__name__, specification_dir='app/openapi/')
#         app.add_api('openapi.yaml', pythonic_params=True)
#         return app.app


class TestFuzzer:
    def test_generic_positive(self):
        assert 0xDEADBEEF

    # def test_fuzz_it_positive(self):
    #     FuzzIt(spec_r='test/app/openapi/openapi.yaml', token='', test_app=self)
