from flask import Flask, render_template, request
from flask_assets import Environment
from flask_socketio import SocketIO, send, emit
import os
import requests

app = Flask(__name__)
#socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
socketio = SocketIO(app, cors_allowed_origins="*", )
assets = Environment(app)
ORION_URL = os.environ.get("ORION_URL", "https://1026-aquarta-bigdataprojecta-oe6lq79ertz.ws-eu110.gitpod.io")
IOTA_NORTH_URL = os.environ.get("IOTA_NORTH_URL", "https://14041-aquarta-bigdataprojecta-oe6lq79ertz.ws-eu110.gitpod.io")

def print_request(r):
    app.logger.info("-"*100)
    app.logger.info(f"request.url: {r.url}")
    app.logger.info(r.headers)
    app.logger.info(f"request.data: {r.data}")
    app.logger.info(f"request.args: {r.args}")
    app.logger.info(f"request.form: {r.form}")
    app.logger.info(f"request.values: {r.values}")
    try:
        app.logger.info(f"request.json: {r.json}")
    except Exception:
        pass
    print(r.method)
    print(r.remote_addr)
    print("="*100)
    return ''

@app.route('/')
def empty():
	return "Hello antonio!"


@app.route("/hello",methods=['GET', 'POST'])
def hello_world():
    print_request(request)
    return ''



@app.route("/oauth2/token",methods=['GET', 'POST'])
def postman_test():
    print_request(request)



@app.route("/perseo_post",methods=['GET', 'POST', 'PUT'])
def perseo_post():
    print_request(request)
    return ''

# Receive a message from the front end HTML
@socketio.on('send_message')
def message_recieved(data):
    app.logger.info(f"MESSAGE RECEIVED PYTHON: {data}")
    emit('message_from_server', {'text':'Message recieved!'})


# Prints the user id
@app.route('/user/<id>')
def user_id(id):
    return str(id)

# Display the HTML Page & pass in a username parameter
@app.route('/html/<username>')
def html(username):
    print(f"username {username}")
    return render_template('index.html', username=username)

def connect_event_callback(*args):
    print('#=> client called {0}'.format(inspect.stack()[0][-4:-2]))

@app.route('/map_update', methods=["PUT"])
def map_update():
    status = request.args['status']
    bridgeid = request.args['bridgeid']
    content_type = request.headers.get('Content-Type')
    app.logger.info(f"status {status}")
    app.logger.info(f"content_type {content_type}")
    app.logger.info(f"request-args {request.args}")
    emit('update_bridge_status', {'bridgeid':bridgeid, "status":status},namespace="/", broadcast=True)
    #emit('update_bridge_status', {'bridgeid':status},)
    return ""

@app.route('/sens_move', methods=["PUT"])
def sens_move():

    sensid = request.json.get('sensid',None)
    if not sensid:
        return "No sensor id!"
    url = IOTA_NORTH_URL+"/iot/devices/"+sensid
    app.logger.info(url)
    res = requests.request(
        "GET",
        url,
        headers={"Accept": "application/json","fiware-service":"openiot", "fiware-servicepath":"/"}
    )


    content_type = request.headers.get('Content-Type')

    app.logger.info(f"response {res.json()}")
    sattrs = res.json().get('static_attributes',None)
    if sattrs:
        bridgeid = None
        for satt in sattrs:
            if satt.get("name") == "refSens" and satt.get("type") == "Relationship":
                bridgeid = satt.get("value")
                break
        if bridgeid:
            url = ORION_URL+"/v2/entities/"+bridgeid+"/attrs/bridge_status"
            app.logger.info(f"Bridge URL  {url}")
            res = requests.request(
                "PUT",
                url,
                json={
                        "type":"Text",
                        "value":"bad"
                    },
                headers={"Accept": "application/json","fiware-service":"openiot"}
            )
            app.logger.info(f"response status code {bridgeid} put {res.status_code}")
            app.logger.info(f"response put {res.content}")
        else:
            return "no bridge"
    return ""

@app.route('/reset_building', methods=["PUT"])
def reset_bridge():
    bridgeid = request.form.get('buildingid',None)
    if bridgeid:
        res = requests.request(
                "PUT",
                ORION_URL+"/v2/entities/"+bridgeid+"/attrs/status",
                json={
                        "type":"Text",
                        "value":"good"
                    },
                headers={"Accept": "application/json","fiware-service":"openiot"}
            )
        app.logger.info(f"response status code put {res.status_code}")
        app.logger.info(f"response put {res.content}")

    return ""

@app.route('/bad_bridge', methods=["PUT"])
def bad_bridge():
    bridgeid = request.form.get('buildingid',None)
    if bridgeid:
        res = requests.request(
                "PUT",
                ORION_URL+"/v2/entities/"+bridgeid+"/attrs/status",
                json={
                        "type":"Text",
                        "value":"bad"
                    },
                headers={"Accept": "application/json","fiware-service":"openiot"}
            )
        app.logger.info(f"response status code put {res.status_code}")
        app.logger.info(f"response put {res.content}")

    return ""


@app.route('/map/')
def map_view():


    res = requests.request(
        "GET",
        ORION_URL+"/v2/entities",
        params={"type":"Bridge"},
        headers={"Accept": "application/json","fiware-service":"openiot"}
    )

    app.logger.info(res)
    app.logger.info(res.text)
    app.logger.info(res.json())
    markers=[]
    for bridge in res.json():
        markers.append({
            'lon':bridge['location']['value']['coordinates'][0],
            'lat':bridge['location']['value']['coordinates'][1],
            "popup":bridge["name"]["value"],
            "status":bridge["status"]["value"],
            "id": bridge["id"],
        })


    return render_template('leaflet.html',  markers=markers)


if __name__ == '__main__':
	#app.run(host='0.0.0.0', port=8000, debug=True)
    socketio.run(app, allow_unsafe_werkzeug=True, host='0.0.0.0', port=8000, debug=True)