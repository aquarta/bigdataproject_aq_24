from flask import (
    current_app, abort, Blueprint, request, Response, make_response, jsonify
)
import model.models as mdl

bp = Blueprint('http_actions', __name__, url_prefix='/http_actions')


@bp.route('/', methods=('GET',))
def http_actions_get() -> Response:
    """Register a new user.

    Returns:
        response: flask.Response object with the application/json mimetype.
    """

    response = make_response(jsonify({
            'status': 'success',
            'data': mdl.HttpAction({}).get_all()
            
        }), 200)

    return response

@bp.route('/', methods=('POST',))
def http_actions_post() -> Response:
    """Register a new email actions.

    Returns:
        response: flask.Response object with the application/json mimetype.
    """
    if not request.is_json:
        logger.info.error("Json expected")
        abort(400)
  
    
    emailact = mdl.HttpAction(request.json)
    res = emailact.add()
    current_app.logger.info(f"http_actions_post {request.json} {res}")
    response = make_response(jsonify({
            'status': 'success',
            'data': res\
        }), 200)
    
    return response

@bp.route('/<object_id>', methods=('PUT',))
def http_actions_put(object_id) -> Response:
    """Register a new email actions.

    Returns:
        response: flask.Response object with the application/json mimetype.
    """

    emailact = mdl.HttpAction({})
    res = emailact.update(object_id, request.json)
    current_app.logger.info(f"http_actions_put {request.json} {res}")
    response = make_response(jsonify({
            'status': 'success',
            'data': res
        }), 200)

    return response


@bp.route('/<object_id>', methods=('DELETE',))
def http_actions_delete(object_id) -> Response:
    """Register a new email actions.

    Returns:
        response: flask.Response object with the application/json mimetype.
    """

    emailact = mdl.HttpAction({})
    res = emailact.update(object_id, request.json)
    current_app.logger.info(f"http_actions_put {request.json} {res}")
    response = make_response(jsonify({
            'status': 'success',
            'data': res
        }), 200)

    return response