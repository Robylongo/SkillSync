import os
import requests
from flask import Blueprint, jsonify, redirect, request, session, url_for

bp = Blueprint('main', __name__)

# generalized response formats
def success_response(data, code=200):
    return jsonify(data), code


def failure_response(message, code=404):
    return jsonify({"error": message}), code

@bp.route('/')
def nuthin():
    return success_response({"message": "Dummy chill backend"})