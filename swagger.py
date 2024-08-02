# app.py

from flask import Flask, jsonify
from flasgger import Swagger, swag_from

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}

swagger_template = {
    "info": {
        "title": "My API",
        "description": "API documentation with Swagger",
        "version": "1.0.0"
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

@app.route('/api/hello', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'A successful response',
            'examples': {
                'application/json': {
                    'message': 'Hello, World!'
                }
            }
        }
    }
})
def hello():
    return jsonify(message='Hello, World!')

@app.route('/api/bye', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'A successful response',
            'examples': {
                'application/json': {
                    'message': 'Hello, World!'
                }
            }
        }
    }
})
def bye():
    return jsonify(message='Bye, World!')


if __name__ == '__main__':
    app.run(debug=True)
