# Simple fuzzer for OpenAPI 3 specification based APIs

## What does this fuzzer do?

1. Sends various attack patterns to all the endpoints defined in the OpenAPI 3 spec file, matching the parameters defined in the specification.
2. Verifies if the response matches those defined in the OAS3 spec file, complains and exit(2) if it doesn't.
3. Complains loudly and exit(1) if an endpoint returns an internal server error (status code 500 and higher)

## Why does this OpenAPI fuzzer exist?

To make it easy to integrate a fuzzer in a CICD pipeline.

It was also quicker to write this than to figure out how other fully featured and complex OAS3 supporting security tools like SoapUI Pro from Smartbear, AppSecInsight from Rapid7 or OWASP ZAP work in a CICD pipeline. 

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
                            DONT_FAIL_ON can be: "nonconformance", which makes the fuzzer exit successfully even if API responses do not match the OAS3 spec file
    ````

## What OAS3 definitions are supported?

1. GET requests to URL's with or without path parameters
1. POST requests to URL's with or without path parameters
2. POST requestBody schemas in application/json containing:
    * string
    * integer
    * number

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
