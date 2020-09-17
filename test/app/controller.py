from flask import make_response, jsonify


def positive_plain(register):
    return make_response(jsonify([]), 200)
