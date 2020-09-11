from src.content.modules import content_blueprint, app

app.register_blueprint(content_blueprint, url_prefix='/api/v1/contents')