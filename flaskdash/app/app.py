from flask import Flask, render_template, request, Response, Blueprint, url_for
from flask_assets import Environment
from flask_socketio import SocketIO, send, emit
import os
import requests
import logging
app = Flask(__name__)
#socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
socketio = SocketIO(app, cors_allowed_origins="*", )
assets = Environment(app)

ORION_URL = os.environ.get("ORION_URL", "http://orion:1026")
IOTA_NORTH_URL = os.environ.get("IOTA_NORTH_URL", "http://iot-agent:14041")

HEIGHT_SENSOR_TYPE_STR = "HeightSensor"
FIWARE_SERVICE = "openiot"
NGSI_PATH = "/"
CONTEXT_URL = "http://context/datamodels.context.jsonld"

api = Blueprint('api',__name__, )
v1_api = Blueprint('v1_api', __name__,url_prefix='/v1')



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


@app.route("/oauth2/token",methods=['GET', 'POST'])
def postman_test():
    print_request(request)



@app.route("/perseo_post",methods=['GET', 'POST', 'PUT'])
def perseo_post():
    print_request(request)
    return ''



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

def get_sensor_attr_from_notification(data, attr_type):
    if data is None:
        return
    for attr in data:
        if attr.get("type",None) == attr_type:
            return attr
    return None


def update_building_status_upsert_strategy(bridgeid):
    url = ORION_URL+"/ngsi-ld/v1/entityOperations/upsert/?options=update"
    app.logger.info(f"Building URL  {url}")
    res = requests.request(
        "POST",
        url,
        json=[
            {
            "@context": CONTEXT_URL,
            "id":bridgeid+"/",
                "type":"Building",
                "BuildingStatus": {
                    "type": "Property",
                    "value": "bad"
                }
            }
            ],
        headers={"Content-Type": "application/ld+json", "Accept": "application/ld+json","NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/"}
    )
    app.logger.info(f"response status code {bridgeid} put {res.status_code}")
    app.logger.info(f"response put {res.content}")

def update_building_status_patch_strategy(bridgeid, status):
    url = ORION_URL+f"/ngsi-ld/v1/entities/{bridgeid}/attrs/BuildingStatus"
    app.logger.info(f"Building URL  {url}")
    res = requests.request(
        "PATCH",
        url,
        json={
        "type": "Property",
        "value": status
        },
        headers={ "Accept": "application/ld+json","NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/","Link":f"<{CONTEXT_URL}>; rel=\"http://www.w3.org/ns/json-ld#context\"; type=\"application/ld+json\""}
    )
    app.logger.info(f"response status code {bridgeid} put {res.status_code}")
    app.logger.info(f"response patch {res.content}")


@v1_api.route('/sens_notify', methods=["POST"])
def sens_move():
    # Expected HeightSensor
    notification_type = request.json.get('type',None)
    sensor_attr = get_sensor_attr_from_notification(request.json.get('data',None), HEIGHT_SENSOR_TYPE_STR)
    # if sensor_attr means that a sensorid is present
    if sensor_attr:
        sensid = sensor_attr.get('id',None)
    else:
        return Response(f"No sensor id {sensid} found.", 404)

    # device_id is internal reference for IOT agent
    device_id = sensid.split(":")[-1]
    if notification_type != "Notification" or  sensor_attr['type'] != HEIGHT_SENSOR_TYPE_STR:
        return Response(f"Wrong type, expected {HEIGHT_SENSOR_TYPE_STR}", 400)
    if not sensid:
        return Response(f"No sensor id {sensid} found.", 404)
    url = IOTA_NORTH_URL+"/iot/devices/"+device_id
    app.logger.info(url)
    res = requests.request(
        "GET",
        url,
        headers={"Accept": "application/ld+json","Fiware-Service":FIWARE_SERVICE,"fiware-servicepath":"/", "NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/"}
    )

    content_type = request.headers.get('Content-Type')

    app.logger.info(f"response {res.json()}")
    sattrs = res.json().get('static_attributes',None)
    if sattrs:
        bridgeid = None
        for satt in sattrs:
            if satt.get("name") == "controlledAsset" and satt.get("type") == "Relationship":
                bridgeid = satt.get("value")
                break
        app.logger.info(f"Bridge id extracted {bridgeid}")
        if bridgeid:
            #update_building_status_upsert_strategy(bridgeid)
            update_building_status_patch_strategy(bridgeid, status="bad")
        else:
            return Response(f"No Building id {bridgeid} found.", 404)
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
                headers={"Accept": "application/json","NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/"}
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
                headers={"Accept": "application/json","NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/"}
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
        headers={"Accept": "application/json","NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/"}
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

# this has to be configured after definition of routes
api.register_blueprint(v1_api, url_prefix='/v1')
app.register_blueprint(api, url_prefix='/api')



if __name__ == '__main__':
	#app.run(host='0.0.0.0', port=8000, debug=True)
    app.logger.setLevel(logging.DEBUG)

    socketio.run(app, allow_unsafe_werkzeug=True, host='0.0.0.0', port=8000, debug=True)