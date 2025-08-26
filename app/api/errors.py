#this is where we will hold a few helper functions to diagnose errors

#IMPORTS
from werkzeug.http import HTTP_STATUS_CODES

#catch-all error handler IMPORTS
from werkzeug.exceptions import HTTPException
from app.api import bp #blueprint import


#ERROR_RESPONSE function - error responses
def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    return payload, status_code

# bad_request function
def bad_request(message):
    return error_response(400, message)

#catch-all error handler
@bp.errorhandler(HTTPException)
def handle_exception(e):
    return error_response(e.code)