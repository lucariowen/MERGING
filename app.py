from werkzeug.middleware.dispatcher import DispatcherMiddleware # use to combine each Flask app into a larger one that is dispatched based on prefix
from __init__ import app as flask_app_login
from inventory import app as flask_app_inventory
from payment import app as flask_app_payment
from rewards import app as flask_app_rewards

application = DispatcherMiddleware(flask_app_login, {
    '/flask_app_inventory': flask_app_inventory,
    '/flask_app_payment': flask_app_payment,
    '/flask_app_rewards': flask_app_rewards,
})

