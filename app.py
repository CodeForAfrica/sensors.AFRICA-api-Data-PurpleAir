from chalice import Chalice
from chalicelib import service


app = Chalice(app_name="sensors-africa-purpleair")


@app.route("/")
def index():
    return {"hello": "world"}


@app.route("/sensors")
def sensors():
    return service.run()
