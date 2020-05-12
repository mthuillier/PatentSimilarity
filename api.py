import logging

import flask
from flasgger import Swagger
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from patent import similarity

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# NOTE this import needs to happen after the logger is configured


# Initialize the Flask application
application = Flask(__name__)

application.config['ALLOWED_EXTENSIONS'] = set(['pdf'])
application.config['CONTENT_TYPES'] = {"pdf": "application/pdf"}
application.config["Access-Control-Allow-Origin"] = "*"


CORS(application)

swagger = Swagger(application)

def clienterror(error):
    resp = jsonify(error)
    resp.status_code = 400
    return resp


def notfound(error):
    resp = jsonify(error)
    resp.status_code = 404
    return resp


@application.route('/patent_similarity', methods=['POST'])
def patent_similarity():
    """Run patent similarity given text.
        ---
        parameters:
          - name: body
            in: body
            schema:
              id: text, top
              required:
                - text
                - top
              properties:
                text:
                  type: string
                  example: a really cool new invention
                top:
                  type: integer
                  default: 1
                  example: 3
            description: Input text and how many top similar patents you want
            required: true
        definitions:
          SimilarityResponse:
            properties:
              patent_id:
                type: string
              text:
                type: string
              cosine:
                type: float
        responses:
          40x:
            description: Client error
          200:
            description: Patent Similarity Response
            example:
                          [
{
  "patent_id": 12345678,
  "text": a really cool old invention,
  "cosine": .134582
},
]
        """
    json_request = request.get_json()
    if not json_request:
        return Response("No json provided.", status=400)
    text = json_request['text']
    top_n = int(json_request['top'])
    if top_n < 1:
        top_n = max(top_n, 1)
    if text is None:
        return Response("No text provided.", status=400)
    else:
        top = similarity(text,top_n)
        result = {}
        for index, row in top.iterrows():
          result[index] = dict(row)
        return flask.jsonify(result)


if __name__ == '__main__':
    application.run(debug=True, use_reloader=True)