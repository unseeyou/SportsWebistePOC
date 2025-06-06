from flask import Flask
from database.database_cmds import Database
from flask_oidc import OpenIDConnect


class CustomApp(Flask):
    def __init__(self, *args, **kwargs):
        super(CustomApp, self).__init__(*args, **kwargs)
        self.config["OIDC_CLIENT_SECRETS"] = "client_secrets.json"
        self.config["OIDC_SCOPES"] = "openid profile"
        self.database: Database = Database()
        self.oidc: OpenIDConnect = OpenIDConnect(self, prefix="/oidc/")
        self.logger.debug("initializing app")


app = CustomApp("app")
