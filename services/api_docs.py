"""Module to handle flask-smorest imports and avoid circular imports"""

from flask_smorest import Blueprint, Api
from marshmallow import Schema, fields

# Re-export commonly used decorators and classes
Blueprint = Blueprint
Api = Api
Schema = Schema
fields = fields
doc = Blueprint.doc
arguments = Blueprint.arguments
response = Blueprint.response

def create_api_docs():
    """Create API documentation components"""
    return {
        'Blueprint': Blueprint,
        'Api': Api,
        'Schema': Schema,
        'fields': fields,
        'doc': doc,
        'arguments': arguments,
        'response': response
    }