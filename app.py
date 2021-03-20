import sentry_sdk

from chalice import Chalice, Rate
from chalicelib import service
from chalicelib.settings import SCHEDULE_RATE, SENTRY_DSN

from sentry_sdk.integrations.chalice import ChaliceIntegration

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[ChaliceIntegration()],
    traces_sample_rate=0.5
)

app = Chalice(app_name="sensors-africa-purpleair")

@app.schedule(Rate(int(SCHEDULE_RATE), unit=Rate.MINUTES))
def scheduled(event):
    return service.run()
