# Simple fuzzer for OpenAPI 3 specification based APIs

## What does this fuzzer do?

1. Sends various attack patterns to all the paths defined in an OpenAPI 3 definition file, using the OAS3 definition to create populate requests.
2. Verifies if the responses matches those defined in the OAS3 definition file, complains and exit(2) if it doesn't.
3. Complains loudly and exit(1) if a path returns an internal server error (status code 500 and higher)

## Why does this OpenAPI fuzzer exist?

To make it easy to integrate an OpenAPI 3 fuzzer in an existing API.

## How do I use this?

1. Install the fuzzer using it's [pip package](https://pypi.org/project/openapi3-fuzzer/)
2. Generate OpenAPI (https://github.com/OpenAPITools/openapi-generator)
3. Create a test_fuzzing file in the test location using the template below:
````python
from openapi3_fuzzer import FuzzIt


def get_token():

    return access_token


class TestvAPI(BaseTestCase):

    def test_fuzzing(self):
        FuzzIt("openapi_location/yaml.yaml", get_token(), self)
````
4. Run using our [unittest container](https://github.com/vwt-digital/cloudbuilder-unittest) or via [Python Unittest Framework](https://docs.python.org/3/library/unittest.html)

## What OAS3 items are supported?

Based on [OpenAPI specification 3.0.2](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md):

Operation | Supported
----------|----------
GET       | Yes
POST      | Yes
PUT       | no
DELETE    | no
OPTIONS   | no
HEAD      | no
PATCH     | no
TRACE     | no

Parameter in | Supported
-------------|----------
path         | Yes
query        | no
header       | no
cookie       | no

Property types | Supported
---------------|----------
string         | Yes
integer        | Yes
number         | Yes
boolean        | no

## Example output

Internal server error:

````
GET fuzzing /managers/expenses/{expenses_id}/attachments

* INTERNAL SERVER ERROR
  Endpoint returned 500 but expected one of [200]
  GET https://dev.myapi.example/managers/expenses/99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999/attachments
````

Response doesn't conform to the OAS3 spec:

````
--------------------------------------------
GET fuzzing /employees/expenses/{expenses_id}

- Unexpected status code
  Endpoint returned 404 but expected one of [200, 'default']
  GET https://dev.myapi.example/employees/expenses/)$#***^
````

````
POST fuzzing /employees/expenses/{expenses_id}

- Unexpected status code
  Endpoint returned 400 but expected one of [201, 'default']
  POST https://dev.myapi.example/employees/expenses
{
    "amount": "123",
    "cost_type": "123",
    "note": ";sleep 10",
    "transaction_date": "123"
}
````

## LICENSE

GPL3
