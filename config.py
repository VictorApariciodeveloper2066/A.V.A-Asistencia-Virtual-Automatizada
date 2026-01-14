from config.default import Config


def init_app(app):
	"""Apply configuration to a Flask `app` instance."""
	app.config.from_object(Config)
