# -*- coding: utf-8 -*-
import os
import tornado.web
import tornado.escape
from karura.environment import Environment
from karura.core.model_manager import ModelManager


class ErrorMessage():

    @classmethod
    def create(cls, message):
        return {
            "error": message
        }

class PingHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("welcome.")

    def post(self):
        body = tornado.escape.json_decode(self.request.body)
        self.write(body)


class TrainingHandler(tornado.web.RequestHandler):

    def post(self):
        """
        dummy = {'messages': {
            'データについて': [{'evaluation': '○', 'message': 'データセットに関する誉め言葉'}], 
            'モデルについて': [{'evaluation': '×', 'message': 'モデルに何か起こった'}], 
            '予測に使用する項目について': [{'evaluation': '-', 'message': '特徴量に関するコメント'}, {'evaluation': '-', 'message': '特徴量に関するコメント2'}]
            }, 'score': 0.8}
        self.write(dummy)
        """
        result = {}
        try:
            body = tornado.escape.json_decode(self.request.body)
            env = Environment()
            model_manager = ModelManager()
            model_manager.build(env, body)
            result = model_manager.get_evaluation()
            model_manager.save()
        except Exception as ex:
            result = ErrorMessage.create(str(ex))

        self.write(result)


class PredictionHandler(tornado.web.RequestHandler):

    def post(self):
        """
        dummy = {
            'prediction': {
                "house_price": 0
            }
        }
        self.write(dummy)
        """
        body = tornado.escape.json_decode(self.request.body)
        result = {}
        try:
            app_id = body["appId"]
            values = body["values"]
            model_manager = ModelManager.load(app_id)
            prediction = model_manager.predict(values)

            result = {
                "prediction": {
                    model_manager.field_manager.target.field_code: prediction
                }
            }
        except Exception as ex:
            result = ErrorMessage.create(str(ex))
        self.write(result)


def application(debug=False):
    app = tornado.web.Application(
        [
            (r"/ping", PingHandler),
            (r"/train", TrainingHandler),
            (r"/predict", PredictionHandler)
        ],
        cookie_secret=os.environ.get("SECRET_TOKEN", "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"),
        debug=debug,
    )
    return app

