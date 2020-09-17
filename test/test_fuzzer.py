from openapi3_fuzzer import FuzzIt
from test import BasePositiveTestCase


class TestvAPI(BasePositiveTestCase):

    def test_fuzz_it_positive(self):
        FuzzIt('test/app/openapi/openapi.yaml', '', self)
