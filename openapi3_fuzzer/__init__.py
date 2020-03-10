import json
import requests
import re
import sys
from prance import ResolvingParser
from time import sleep


def do_post_req(ep, headers, payload):
    """
    Perform an actual POST request
    returns the response object r
    """
    try:
        # print("--- Starting POST request to {}".format(ep))
        sleep(0.05)
        r = requests.post('{}'.format(ep), data=payload, headers=headers, timeout=20, allow_redirects=False)
    except Exception as e:
        print("    Exception connecting to {} with {}".format(ep, str(e)))
        return ({"status_code": -1, "content": ""})
    else:
        # print("    POST request to {} returned status {}: {}".format(ep, r.status_code, r.content))
        return r


def do_get_req(ep, headers):
    """
    Perform an actual GET request
    returns the response object r
    """
    try:
        # print("--- Starting GET request to {}".format(ep))
        sleep(0.05)
        r = requests.get('{}'.format(ep), headers=headers, timeout=20, allow_redirects=False)
    except Exception as e:
        print("    Exception connecting to {} with {}".format(ep, str(e)))
        return ({"status_code": -1, "content": ""})
    else:
        # print("    GET request to {} returned status {}: {}".format(ep,r.status_code, r.content))
        return (r)


def get_happyday_pattern(datatype):
    try:
        fuzzdbfile = "openapi3_fuzzer/fuzz-{}.txt".format(re.sub(r'[^a-zA-Z]', '', datatype))
        if re.sub(r'[^a-zA-Z]', '', datatype) == 'object':
            fuzzdbfile = "openapi3_fuzzer/fuzz-fallback.txt"
    except FileNotFoundError:
        fuzzdbfile = "openapi3_fuzzer/fuzz-fallback.txt"
    happydaystring = open(fuzzdbfile).readlines()[0].rstrip()
    return happydaystring


def get_fuzz_patterns(datatype):
    fuzzdbfile = "openapi3_fuzzer/fuzz-{}.txt".format(re.sub(r'[^a-zA-Z]', '', datatype))
    try:
        lines = open(fuzzdbfile).readlines()
    except FileNotFoundError:
        fuzzdbfile = "openapi3_fuzzer/fuzz-fallback.txt"
        lines = open(fuzzdbfile).readlines()
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
            url = url.replace("{{{}}}".format(pathvar.get("name")), happydaystring.rstrip())
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
                url = url.replace("{{{}}}".format(pathvar.get("name")), line.rstrip())
                for otherpathvar in pathvars:
                    datatype = otherpathvar.get("schema", {}).get("type", "fallback")
                    happydaystring = get_happyday_pattern(datatype)
                    url = url.replace("{{{}}}".format(otherpathvar.get("name")), happydaystring.rstrip())
                urls.add(url)
    return urls


def generate_payloads_from_postvars(postvars):
    """
    From a given OAS3 dict of requestBody variables
    generate a list of payload dicts
    """
    payloads = []
    payload = {}

    for jsontype in ["int", "str", "arr", "none"]:
        for fuzzparam in postvars.keys():
            datatype = postvars.get(fuzzparam, {}).get("type", "fallback")
            lines = get_fuzz_patterns(datatype)
            for line in lines:
                payload = {}
                for param in postvars.keys():
                    datatype = postvars.get(param, {}).get("type", "")
                    happydaystring = get_happyday_pattern(datatype)
                    if param == fuzzparam:
                        if jsontype == "int" or datatype == "int" or datatype == "number":
                            try:
                                payload[param] = int(line.rstrip())
                            except ValueError:
                                payload[param] = line.rstrip()
                        elif jsontype == "str":
                            payload[param] = line.rstrip()
                        elif jsontype == "arr":
                            payload[param] = [line.rstrip()]
                        elif jsontype == "none":
                            payload[param] = None
                    else:
                        if datatype == "int" or datatype == "number":
                            try:
                                payload[param] = int(happydaystring)
                            except ValueError:
                                payload[param] = happydaystring
                        else:
                            payload[param] = happydaystring
                payloads.append(payload)
    payloads_uniq = []
    for payload in payloads:
        if payload not in payloads_uniq:
            payloads_uniq.append(payload)
    return payloads_uniq


def do_post_fuzzing(*args, **kwargs):
    baseurl = kwargs.get('baseurl', "")
    headers = kwargs.get('headers', {})
    path = kwargs.get('path', None)
    pathvars = kwargs.get('pathvars', {})
    postvars = kwargs.get('postvars', {})
    responses = kwargs.get('responses', [])

    newresponses = []
    for response in responses:
        try:
            newresponses.append(int(response))
        except ValueError:
            newresponses.append(response)
    responses = newresponses

    url = generate_happy_day_url_from_pathvars(baseurl, path, pathvars)
    payloads = generate_payloads_from_postvars(postvars)
    stats = {}
    stats['path'] = path
    stats['method'] = 'POST'

    for payload in payloads:
        r = do_post_req(url, headers, payload)
        try:
            stats[r.status_code] = stats[r.status_code] + 1
        except KeyError:
            stats[r.status_code] = 1
        if (r.status_code not in responses) and r.status_code < 500:
            print(
                "\n- Unexpected status code\n  Endpoint returned {} but expected one of {}\n  POST {}\n{}"
                .format(r.status_code, responses,
                        url, json.dumps(payload,
                                        indent=4)))
        elif r.status_code >= 500:
            print(
                "\n* INTERNAL SERVER ERROR\n  Endpoint returned {} but expected one of {}\n  POST {}\n{}"
                .format(r.status_code, responses,
                        url, json.dumps(payload,
                                        indent=4)))
    return stats


def do_get_fuzzing(*args, **kwargs):
    """
    Perform fuzzing on a GET endpoint
    """
    baseurl = kwargs.get('baseurl', "")
    headers = kwargs.get('headers', {})
    path = kwargs.get('path', None)
    pathvars = kwargs.get('pathvars', {})
    responses = kwargs.get('responses', [])

    urls = generate_urls_from_pathvars(baseurl, path, pathvars)
    stats = {}
    stats['path'] = path
    stats['method'] = 'GET'

    newresponses = []
    for response in responses:
        try:
            newresponses.append(int(response))
        except ValueError:
            newresponses.append(response)
    responses = newresponses

    for url in urls:
        r = do_get_req(url, headers)
        try:
            stats[r.status_code] = stats[r.status_code] + 1
        except KeyError:
            stats[r.status_code] = 1
        if (r.status_code not in responses) and r.status_code < 500:
            print("\n- Unexpected status code\n  Endpoint returned {} but expected one of {}\n  GET {}".format(r.status_code, responses,
                                                                                                               url))
            try:
                stats["nonconformance"] = stats["nonconformance"] + 1
            except KeyError:
                stats["nonconformance"] = 1
        elif r.status_code >= 500:
            print(
                "\n* INTERNAL SERVER ERROR\n  Endpoint returned {} but expected one of {}\n  GET {}".format(r.status_code, responses, url))
            try:
                stats["internalservererror"] = stats["internalservererror"] + 1
            except KeyError:
                stats["internalservererror"] = 1

    return stats


class Fuzzer:

    def __init__(self, spec: str, token: str):

        baseurl = ''
        specurl = spec
        headers = {"Authorization": f"Bearer {token}",
                   "Content-type": "application/json"}

        parser = ResolvingParser(specurl)
        spec = parser.specification  # contains fully resolved specs as a dict
        # print(json.dumps(parser.specification.get("paths").get("/employees/expenses/{expenses_id}/attachments").get("post"),indent=2))
        allstats = []
        for path, pathvalues in spec.get("paths", {}).items():
            for method, methodvalues in pathvalues.items():
                pathvars = {}
                postvars = {}
                if method == 'get':
                    if 'parameters' in methodvalues.keys():
                        pathvars = methodvalues.get("parameters", {})
                        responses = list(methodvalues.get("responses", {}).keys())
                        print("--------------------------------------------")
                        print("GET fuzzing {}".format(path))
                        stats = do_get_fuzzing(baseurl=baseurl, headers=headers, path=path, pathvars=pathvars, responses=responses)
                        allstats.append(stats)
                if method == 'post':
                    responses = list(methodvalues.get("responses", {}).keys())
                    if 'requestBody' in methodvalues.keys() and 'parameters' in methodvalues.keys():
                        pathvars = methodvalues.get("parameters")
                        postvars = methodvalues.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema",
                                                                                                                          {}).get(
                            "properties", {})
                        print("--------------------------------------------")
                        print("POST fuzzing param URL {}:".format(path))
                        stats = do_post_fuzzing(baseurl=baseurl, headers=headers, path=path, pathvars=pathvars, postvars=postvars,
                                                responses=responses)
                        allstats.append(stats)
                    elif 'requestBody' in methodvalues.keys():
                        postvars = methodvalues.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema",
                                                                                                                          {}).get(
                            "properties", {})
                        print("--------------------------------------------")
                        print("POST fuzzing non-param URL {}:".format(path))
                        stats = do_post_fuzzing(baseurl=baseurl, headers=headers, path=path, postvars=postvars, responses=responses)
                        allstats.append(stats)
                sys.stdout.flush()

        print("============================================")
        print(json.dumps(allstats, indent=2))

        if any('internalservererror' in d for d in allstats):
            exit(1)
        elif any('nonconformance' in d for d in allstats):
            exit(2)
        else:
            exit(0)
