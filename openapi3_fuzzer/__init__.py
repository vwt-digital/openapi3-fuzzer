import requests
import re
from prance import ResolvingParser
from time import sleep


class _ProtectFuzz:

    def do_post_req(self, app, ep, headers, payload):
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

    def do_get_req(self, app, ep, headers):
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
            return r

    def get_happyday_pattern(self, datatype):
        try:
            fuzzdbfile = "fuzz-{}.txt".format(re.sub(r'[^a-zA-Z]', '', datatype))
            if re.sub(r'[^a-zA-Z]', '', datatype) == 'object':
                fuzzdbfile = "fuzz-fallback.txt"
        except FileNotFoundError:
            fuzzdbfile = "fuzz-fallback.txt"
        happydaystring = open(fuzzdbfile).readlines()[0].rstrip()
        return happydaystring

    def get_fuzz_patterns(self, datatype):
        fuzzdbfile = "fuzz-{}.txt".format(re.sub(r'[^a-zA-Z]', '', datatype))
        try:
            lines = open(fuzzdbfile).readlines()
        except FileNotFoundError:
            fuzzdbfile = "fuzz-fallback.txt"
            lines = open(fuzzdbfile).readlines()
        return lines

    def generate_happy_day_url_from_pathvars(self, baseurl, path, pathvars):
        """
        From a given OAS3 endpoint with path parameters,
        generate 1 URL while substituting all params with happy day strings
        """
        url = "{}{}".format(baseurl, path)
        if pathvars is not None:
            for pathvar in pathvars:
                datatype = pathvar.get("schema", {}).get("type", "fallback")
                happydaystring = self.get_happyday_pattern(datatype)
                url = url.replace("{{{}}}".format(pathvar.get("name")), happydaystring.rstrip())
        return url

    def generate_urls_from_pathvars(self, baseurl, path, pathvars):
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
                lines = self.get_fuzz_patterns(datatype)
                for line in lines:
                    url = "{}{}".format(baseurl, path)
                    url = url.replace("{{{}}}".format(pathvar.get("name")), line.rstrip())
                    for otherpathvar in pathvars:
                        datatype = otherpathvar.get("schema", {}).get("type", "fallback")
                        happydaystring = self.get_happyday_pattern(datatype)
                        url = url.replace("{{{}}}".format(otherpathvar.get("name")), happydaystring.rstrip())
                    urls.add(url)
        return urls

    def generate_payloads_from_postvars(self, postvars):
        """
        From a given OAS3 dict of requestBody variables
        generate a list of payload dicts
        """
        payloads = []
        payload = {}

        for jsontype in ["int", "str", "arr", "none"]:
            for fuzzparam in postvars.keys():
                datatype = postvars.get(fuzzparam, {}).get("type", "fallback")
                lines = self.get_fuzz_patterns(datatype)
                for line in lines:
                    payload = {}
                    for param in postvars.keys():
                        datatype = postvars.get(param, {}).get("type", "")
                        happydaystring = self.get_happyday_pattern(datatype)
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

    def do_post_fuzzing(self, *args, **kwargs):
        baseurl = kwargs.get('baseurl', "")
        headers = kwargs.get('headers', {})
        path = kwargs.get('path', None)
        pathvars = kwargs.get('pathvars', {})
        postvars = kwargs.get('postvars', {})
        responses = kwargs.get('responses', [])
        app = kwargs.get('app', None)

        newresponses = []
        for response in responses:
            try:
                newresponses.append(int(response))
            except ValueError:
                newresponses.append(response)
        responses = newresponses

        url = self.generate_happy_day_url_from_pathvars(baseurl, path, pathvars)
        payloads = self.generate_payloads_from_postvars(postvars)

        for payload in payloads:
            with app.subTest(method="POST", url=url, payload=payload,
                             headers=headers):
                r = self.do_post_req(app, url, headers, payload)
                app.assertLess(r.status_code, 500)
                app.assertIn(r.status_code, responses)
        return True

    def do_get_fuzzing(self, *args, **kwargs):
        """
        Perform fuzzing on a GET endpoint
        """
        baseurl = kwargs.get('baseurl', "")
        headers = kwargs.get('headers', {})
        path = kwargs.get('path', None)
        pathvars = kwargs.get('pathvars', {})
        responses = kwargs.get('responses', [])
        app = kwargs.get('app', None)

        urls = self.generate_urls_from_pathvars(baseurl, path, pathvars)
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
            with app.subTest(method="GET", url=url, headers=headers):
                r = self.do_get_req(app, url, headers)
                app.assertLess(r.status_code, 500)
                app.assertIn(r.status_code, responses)
        return True


class FuzzIt:

    def __init__(self, spec_r: str, token: str, app):

        baseurl = ''
        specurl = spec_r
        headers = {"Authorization": f"Bearer {token}",
                   "Content-type": "application/json"}

        parser = ResolvingParser(specurl)
        spec = parser.specification
        for path, pathvalues in spec.get("paths", {}).items():
            for method, methodvalues in pathvalues.items():
                if method == 'get':
                    if 'parameters' in methodvalues.keys():
                        pathvars = methodvalues.get("parameters", {})
                        responses = list(methodvalues.get("responses", {}).keys())
                        print("--------------------------------------------")
                        print("GET fuzzing {}".format(path))
                        _ProtectFuzz.do_get_fuzzing(app=app, baseurl=baseurl,
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
                        print("--------------------------------------------")
                        print("POST fuzzing param URL {}:".format(path))
                        _ProtectFuzz.do_post_fuzzing(app=app, baseurl=baseurl,
                                                     headers=headers, path=path,
                                                     pathvars=pathvars, postvars=postvars,
                                                     responses=responses)
                    elif 'requestBody' in methodvalues.keys():
                        postvars = methodvalues.get("requestBody", {}).get(
                            "content", {}).get("application/json", {}).get(
                            "schema", {}).get("properties", {})
                        print("--------------------------------------------")
                        print("POST fuzzing non-param URL {}:".format(path))
                        _ProtectFuzz.do_post_fuzzing(app=app, baseurl=baseurl,
                                                     headers=headers, path=path,
                                                     postvars=postvars, responses=responses)
