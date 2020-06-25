from flask_testing import TestCase
import json
import os
import re
from time import sleep
from typing import List, Dict
from prance import ResolvingParser


def do_post_req(mytestcase, ep, headers, payload):
    """
    Perform an actual POST request
    returns the response object r
    """
    self = mytestcase
    try:
        # print("--- Starting POST request to {}".format(ep))
        sleep(0.05)
        r = self.client.open(
            ep,
            method='POST',
            data=json.dumps(payload),
            headers=headers)
    except Exception as e:
        print("Exception connecting to {} with {}".format(ep, str(e)))
        return {"status_code": -1, "content": ""}
    else:
        return r


def do_get_req(mytestcase, ep, headers):
    """
    Perform an actual GET request
    returns the response object r
    """
    self = mytestcase
    try:
        # print("--- Starting GET request to {}".format(ep))
        sleep(0.05)
        r = self.client.open(
            ep,
            method='GET',
            headers=headers)
    except Exception as e:
        print("    Exception connecting to {} with {}".format(ep, str(e)))
        return {"status_code": -1, "content": ""}
    else:
        return r


def do_head_req(mytestcase, ep, headers):
    """
    Perform an actual HEAD request
    returns the response object r
    """
    self = mytestcase
    try:
        # print("--- Starting HEAD request to {}".format(ep))
        sleep(0.05)
        r = self.client.open(
            ep,
            method='HEAD',
            headers=headers)
    except Exception as e:
        print("    Exception connecting to {} with {}".format(ep, str(e)))
        return {"status_code": -1, "content": ""}
    else:
        return r


def do_delete_req(mytestcase, ep, headers):
    """
    Perform an actual DELETE request
    returns the response object r
    """
    self = mytestcase
    try:
        # print("--- Starting DELETE request to {}".format(ep))
        sleep(0.05)
        r = self.client.open(
            ep,
            method='DELETE',
            headers=headers)
    except Exception as e:
        print("    Exception connecting to {} with {}".format(ep, str(e)))
        return {"status_code": -1, "content": ""}
    else:
        return r


def do_put_req(mytestcase, ep, headers, payload):
    """
    Perform an actual POST request
    returns the response object r
    """
    self = mytestcase
    try:
        # print("--- Starting POST request to {}".format(ep))
        sleep(0.05)
        r = self.client.open(
            ep,
            method='PUT',
            data=json.dumps(payload),
            headers=headers)
    except Exception as e:
        print("Exception connecting to {} with {}".format(ep, str(e)))
        return {"status_code": -1, "content": ""}
    else:
        return r


def get_happyday_pattern(datatype):
    fuzzdbfile = "{}/fuzz/fuzz-{}.txt".format(os.path.dirname(os.path.realpath(__file__)),
                                              re.sub(r'[^a-zA-Z]', '', datatype))
    fuzzdbfallbackfile = "{}/fuzz/fuzz-fallback.txt".format(os.path.dirname(os.path.realpath(__file__)))
    happydaystring = ""
    if os.path.exists(fuzzdbfile):
        with open(fuzzdbfile) as f:
            happydaystring = f.readlines()[0].rstrip()
    elif os.path.exists(fuzzdbfallbackfile):
        with open(fuzzdbfallbackfile) as f:
            happydaystring = f.readlines()[0].rstrip()
    else:
        happydaystring = "AAAAAAAAAstaticfallbackoffallbackstring"
        raise FileNotFoundError
    return happydaystring


def get_fuzz_patterns(datatype):
    fuzzdbfile = "{}/fuzz/fuzz-{}.txt".format(os.path.dirname(os.path.realpath(__file__)),
                                              re.sub(r'[^a-zA-Z]', '', datatype))
    fuzzdbfallbackfile = "{}/fuzz/fuzz-fallback.txt".format(os.path.dirname(os.path.realpath(__file__)))
    lines = []
    if os.path.exists(fuzzdbfile):
        with open(fuzzdbfile) as f:
            lines = f.readlines()
    elif os.path.exists(fuzzdbfallbackfile):
        with open(fuzzdbfallbackfile) as f:
            lines = f.readlines()
    else:
        lines = "AAAAAAAAAstaticfallbackoffallbackstring"
        raise FileNotFoundError
    return lines


def generate_happy_day_url_from_pathvars(baseurl, path, pathvars):
    """
    From a given OAS3 endpoint with path parameters,
    generate 1 URL while substituting all params with happy day strings
    """
    url = "{}{}".format(baseurl, path)
    if pathvars is not None:
        for pathvar in pathvars:
            datatype = pathvar.get("schema", {}).get("type", "fallback")
            happydaystring = get_happyday_pattern(datatype)
            url = url.replace("{{{}}}".format(
                pathvar.get("name")), happydaystring.rstrip())
    return url


def generate_urls_from_pathvars(baseurl, path, pathvars):
    """
    From a given OAS3 endpoint with path parameters,
    generate all the possible URLs to fuzz
    while only substituting 1 param with all fuzzing entries
    and using happy day strings for the other parameters
    """
    urls = set()
    for pathvar in pathvars:
        if pathvar.get('in', None) == 'path' and 'name' in pathvar.keys():
            datatype = pathvar.get("schema", {}).get("type", "fallback")
            lines = get_fuzz_patterns(datatype)
            for line in lines:
                url = "{}{}".format(baseurl, path)
                url = url.replace("{{{}}}".format(
                    pathvar.get("name")), line.rstrip())
                for otherpathvar in pathvars:
                    datatype = otherpathvar.get(
                        "schema", {}).get("type", "fallback")
                    happydaystring = get_happyday_pattern(datatype)
                    url = url.replace("{{{}}}".format(
                        otherpathvar.get("name")), happydaystring.rstrip())
                urls.add(url)
    return urls


def generate_payloads_from_request_vars(request_vars: dict) -> List[Dict[str, str]]:
    """
    generate_payloads_from_request_vars: Generate payloads for every datatype in fuzz_types
    From a given OAS3 dict of requestBody variables
    generate a list of payload dicts
    @param request_vars: dict of requestBody variables
    @return: list of payload dicts
    """
    FUZZ_TYPES = ["int", "str", "arr", "none"]  # constant list of types to generate from
    payloads = []
    payload = {}

    for fuzz_type in FUZZ_TYPES:
        for request_key, request_value in request_vars.items():
            data_type = request_value.get("type", "")
            fuzz_patterns = get_fuzz_patterns(data_type)
            for fuzz_pattern in fuzz_patterns:
                payload = {}
                for param_key, param_value in request_vars.items():
                    data_type = param_value.get("type", "")
                    happy_day_string = get_happyday_pattern(data_type)

                    if param_key == request_key:
                        # fuzz both data type and fuzz type
                        if fuzz_type == "int" or data_type == "int" or data_type == "number":
                            try:
                                payload[param_key] = int(fuzz_pattern.rstrip())
                            except ValueError:
                                payload[param_key] = fuzz_pattern.rstrip()
                        elif fuzz_type == "str":
                            payload[param_key] = fuzz_pattern.rstrip()
                        elif fuzz_type == "arr":
                            payload[param_key] = fuzz_pattern.rstrip()
                        elif fuzz_type == "none":
                            payload[param_key] = fuzz_pattern.rstrip()
                        else:
                            if data_type == "int" or data_type == "number":
                                try:
                                    payload[param_key] = int(happy_day_string)
                                except ValueError:
                                    payload[param_key] = happy_day_string
                            else:
                                payload[param_key] = happy_day_string
                payloads.append(payload)
    payloads_unique = []
    for payload in payloads:
        if payload not in payloads_unique:
            payloads_unique.append(payload)
    return payloads_unique


def do_post_fuzzing(*args, **kwargs):
    base_url = kwargs.get('baseurl', "")
    headers = kwargs.get('headers', {})
    path = kwargs.get('path', None)
    path_vars = kwargs.get('pathvars', {})
    post_vars = kwargs.get('postvars', {})
    responses = kwargs.get('responses', [])
    test_case = kwargs.get('mytestcase', None)

    new_responses = []
    for response in responses:
        try:
            new_responses.append(int(response))
        except ValueError:
            new_responses.append(response)
    responses = new_responses

    # Generate url once
    url = generate_happy_day_url_from_pathvars(base_url, path, path_vars)
    payloads = generate_payloads_from_request_vars(post_vars)

    # And send multiple payloads
    for payload in payloads:
        with test_case.subTest(method="POST", url=url, payload=payload,
                               headers=headers):
            result = do_post_req(test_case, url, headers, payload)
            test_case.assertLess(result.status_code, 500)
            test_case.assertIn(result.status_code, responses)
    return True


def do_get_fuzzing(*args, **kwargs):
    """
    Perform fuzzing on a GET endpoint
    """
    baseurl = kwargs.get('baseurl', "")
    headers = kwargs.get('headers', {})
    path = kwargs.get('path', None)
    pathvars = kwargs.get('pathvars', {})
    responses = kwargs.get('responses', [])
    test_case = kwargs.get('mytestcase', None)

    newresponses = []
    for response in responses:
        try:
            newresponses.append(int(response))
        except ValueError:
            newresponses.append(response)
    responses = newresponses

    urls = generate_urls_from_pathvars(baseurl, path, pathvars)

    for url in urls:
        with test_case.subTest(method="GET", url=url, headers=headers):
            result = do_get_req(test_case, url, headers)
            test_case.assertLess(result.status_code, 500)
            test_case.assertIn(result.status_code, responses)
    return True


def do_head_fuzzing(*args, **kwargs):
    """
    Perform fuzzing on a HEAD endpoint
    """
    baseurl = kwargs.get('baseurl', "")
    headers = kwargs.get('headers', {})
    path = kwargs.get('path', None)
    pathvars = kwargs.get('pathvars', {})
    responses = kwargs.get('responses', [])
    test_case = kwargs.get('mytestcase', None)

    newresponses = []
    for response in responses:
        try:
            newresponses.append(int(response))
        except ValueError:
            newresponses.append(response)
    responses = newresponses

    urls = generate_urls_from_pathvars(baseurl, path, pathvars)

    for url in urls:
        with test_case.subTest(method="HEAD", url=url, headers=headers):
            result = do_head_req(test_case, url, headers)
            test_case.assertLess(result.status_code, 500)
            test_case.assertIn(result.status_code, responses)
    return True


def do_delete_fuzzing(*args, **kwargs):
    """
    Perform fuzzing on a DELETE endpoint
    """
    baseurl = kwargs.get('baseurl', "")
    headers = kwargs.get('headers', {})
    path = kwargs.get('path', None)
    pathvars = kwargs.get('pathvars', {})
    responses = kwargs.get('responses', [])
    test_case = kwargs.get('mytestcase', None)

    newresponses = []
    for response in responses:
        try:
            newresponses.append(int(response))
        except ValueError:
            newresponses.append(response)
    responses = newresponses

    urls = generate_urls_from_pathvars(baseurl, path, pathvars)

    for url in urls:
        with test_case.subTest(method="DELETE", url=url, headers=headers):
            result = do_delete_req(test_case, url, headers)
            test_case.assertLess(result.status_code, 500)
            test_case.assertIn(result.status_code, responses)
    return True


def do_put_fuzzing(*args, **kwargs):
    """
    Perform fuzzing on a PUT endpoint
    """
    baseurl = kwargs.get('baseurl', "")
    headers = kwargs.get('headers', {})
    path = kwargs.get('path', None)
    pathvars = kwargs.get('pathvars', {})
    putvars = kwargs.get('putvars', {})
    responses = kwargs.get('responses', [])
    test_case = kwargs.get('mytestcase', None)

    newresponses = []
    for response in responses:
        try:
            newresponses.append(int(response))
        except ValueError:
            newresponses.append(response)
    responses = newresponses

    url = generate_happy_day_url_from_pathvars(baseurl, path, pathvars)

    payloads = generate_payloads_from_request_vars(putvars)
    for payload in payloads:
        with test_case.subTest(method="PUT", url=url, payload=payload,
                               headers=headers):
            result = do_put_req(test_case, url, headers, payload)
            test_case.assertLess(result.status_code, 500)
            test_case.assertIn(result.status_code, responses)
    return True


def do_fuzzing(my_testcase: TestCase, headers: Dict[str, str], spec_r: str):
    self = my_testcase
    baseurl = ""

    fuzz_count = 0

    parser = ResolvingParser(spec_r)
    spec = parser.specification  # contains fully resolved specs as a dict
    for path, pathvalues in spec.get("paths", {}).items():
        for method, methodvalues in pathvalues.items():
            fuzz_count += 1

            pathvars = {}
            if method == 'get':
                if 'parameters' in methodvalues.keys():
                    pathvars = methodvalues.get("parameters", {})
                    responses = list(methodvalues.get("responses", {}).keys())
                    do_get_fuzzing(mytestcase=self, baseurl=baseurl,
                                   headers=headers, path=path,
                                   pathvars=pathvars, responses=responses)
            if method == 'head':
                if 'parameters' in methodvalues.keys():
                    pathvars = methodvalues.get("parameters", {})
                    responses = list(methodvalues.get("responses", {}).keys())
                    do_head_fuzzing(mytestcase=self, baseurl=baseurl,
                                    headers=headers, path=path,
                                    pathvars=pathvars, responses=responses)

            if method == 'delete':
                if 'parameters' in methodvalues.keys():
                    pathvars = methodvalues.get("parameters", {})
                    responses = list(methodvalues.get("responses", {}).keys())
                    do_delete_fuzzing(mytestcase=self, baseurl=baseurl,
                                      headers=headers, path=path,
                                      pathvars=pathvars, responses=responses)
            if method == 'post':
                responses = list(methodvalues.get("responses", {}).keys())
                if 'requestBody' in methodvalues.keys() and \
                        'parameters' in methodvalues.keys():
                    pathvars = methodvalues.get("parameters")
                    postvars = methodvalues.get("requestBody", {}).get(
                        "content", {}).get("application/json", {}).get(
                        "schema", {}).get("properties", {})
                    do_post_fuzzing(mytestcase=self, baseurl=baseurl,
                                    headers=headers, path=path,
                                    pathvars=pathvars, postvars=postvars,
                                    responses=responses)
                elif 'requestBody' in methodvalues.keys():
                    postvars = methodvalues.get("requestBody", {}).get(
                        "content", {}).get("application/json", {}).get(
                        "schema", {}).get("properties", {})
                    do_post_fuzzing(mytestcase=self, baseurl=baseurl,
                                    headers=headers, path=path,
                                    postvars=postvars, responses=responses)
            if method == 'put':
                responses = list(methodvalues.get("responses", {}).keys())
                if all(key in methodvalues.keys() for key in ['requestBody', 'parameters']):
                    pathvars = methodvalues.get("parameters")
                    putvars = methodvalues.get("requestBody", {}).get(
                        "content", {}).get("application/json", {}).get(
                        "schema", {}).get("properties", {})
                    do_put_fuzzing(mytestcase=self, baseurl=baseurl,
                                   headers=headers, path=path,
                                   pathvars=pathvars, putvars=putvars,
                                   responses=responses)
                elif 'requestBody' in methodvalues.keys():
                    putvars = methodvalues.get("requestBody", {}).get(
                        "content", {}).get("application/json", {}).get(
                        "schema", {}).get("properties", {})
                    do_put_fuzzing(mytestcase=self, baseurl=baseurl,
                                   headers=headers, path=path,
                                   putvars=putvars, responses=responses)
            else:
                fuzz_count -= 1  # method in spec is not fuzzed
    print("Fuzzed " + str(fuzz_count) + " endpoints")


class FuzzIt:
    def __init__(self, spec_r: str, token: str, test_app: TestCase, header_addition: Dict[str, str] = None):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        if header_addition is not None and isinstance(header_addition, dict):
            for key, value in header_addition.items():
                headers[key] = value
        do_fuzzing(test_app, headers, spec_r)
