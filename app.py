from chalice import Chalice, Rate
from chalicelib import service


app = Chalice(app_name="sensors-africa-purpleair")

@app.schedule(Rate(10, unit=Rate.MINUTES))
def scheduled(event):
    return service.run()
