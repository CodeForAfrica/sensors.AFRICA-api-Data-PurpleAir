from chalice import Chalice
from chalicelib import purple_api, settings


app = Chalice(app_name='sensors-africa-purpleair')


@app.route('/')
def index():
    return {'hello': 'world'}

@app.route('/sensors')
def sensors():
    return purple_api.run()
