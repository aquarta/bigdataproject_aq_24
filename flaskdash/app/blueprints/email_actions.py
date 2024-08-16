from flask import (
    current_app, abort, Blueprint, request, Response, make_response, jsonify
)
import model.models as mdl

bp = Blueprint('email_actions', __name__, url_prefix='/email_actions')


@bp.route('/', methods=('GET',))
def email_actions_get() -> Response:
    """Register a new user.

    Returns:
        response: flask.Response object with the application/json mimetype.
    """

    response = make_response(jsonify({
            'status': 'success',
            'data': mdl.EmailAction({}).get_all()
            
        }), 200)

    return response

@bp.route('/', methods=('POST',))
def email_actions_post() -> Response:
    """Register a new email actions.

    Returns:
        response: flask.Response object with the application/json mimetype.
    """
    if not request.is_json:
        abort(400)
  
    
    emailact = mdl.EmailAction(request.json)
    res = emailact.add()
    current_app.logger.info(f"email_actions_post {request.json} {res}")
    response = make_response(jsonify({
            'status': 'success',
            'data': res\
        }), 200)
    
    return response

@bp.route('/<object_id>', methods=('PUT',))
def email_actions_put(object_id) -> Response:
    """Register a new email actions.

    Returns:
        response: flask.Response object with the application/json mimetype.
    """

    emailact = mdl.EmailAction({})
    res = emailact.update(object_id, request.json)
    current_app.logger.info(f"email_actions_put {request.json} {res}")
    response = make_response(jsonify({
            'status': 'success',
            'data': res
        }), 200)

    return response


@bp.route('/<object_id>', methods=('DELETE',))
def email_actions_put(object_id) -> Response:
    """Delete

    Returns:
        response: flask.Response object with the application/json mimetype.
    """

    emailact = mdl.EmailAction({})
    res = emailact.update(object_id, request.json)
    current_app.logger.info(f"email_actions_put {request.json} {res}")
    response = make_response(jsonify({
            'status': 'success',
        }), 200)

    return response