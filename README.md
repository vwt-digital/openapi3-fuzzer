# Simple fuzzer for OpenAPI 3 specification based APIs

## What does this fuzzer do?

1. Sends various attack patterns to all the paths defined in an OpenAPI 3 definition file, using the OAS3 definition to create populate requests.
2. Verifies if the responses matches those defined in the OAS3 definition file, complains and exit(2) if it doesn't.
3. Complains loudly and exit(1) if a path returns an internal server error (status code 500 and higher)

## Why does this OpenAPI fuzzer exist?

To make it easy to integrate a OpenAPI 3 fuzzer in a CICD pipeline.

## How do I use this?

1. git clone https://github.com/jorritfolmer/openapi3-fuzzer.git
1. virtualenv venv
1. source venv/bin/activate
1. pip install -r requirements.txt
1. python openapi3-fuzzer.py --help
    ````
    usage: openapi3-fuzzer.py [-h] [--auth AUTH] [--dont_fail_on DONT_FAIL_ON]
                            base_url oas3spec_url

    positional arguments:
    base_url              Base URL of the OAS3 API, e.g.
                            https://dev.myapi.example, without trailing slash
    oas3spec_url          URL to fetch the OpenAPI3 spec file from, e.g.
                            https://dev.myapi.example/openapi.json

    optional arguments:
    -h, --help            show this help message and exit
    --auth AUTH           Authorization header field, e.g. "Bearer
                            longbase64string", or "Basic shortb64string"
    --dont_fail_on DONT_FAIL_ON
                            DONT_FAIL_ON can be: "nonconformance", which makes
                            the fuzzer exit successfully even if API responses
                            do not match the OAS3 spec file
    ````

Example:

```
python openapi3-fuzzer https://dev.myapi.example \
    https://dev.myapi.example/openapi.json \
    --auth "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
```

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
