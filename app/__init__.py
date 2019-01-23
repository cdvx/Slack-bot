
from re import match

from flask import jsonify, request

from app.actions import Actions
from app.utils.slackhelper import SlackHelper
from config.env import app_env
from flask_api import FlaskAPI

allowed_commands = [
   'show-task',
   'show-tasks',
   'my-task',
   'my-tasks',
   'help',
   "write"
]

def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=False)
    app.config.from_object(app_env[config_name])
    app.config.from_pyfile("../config/env.py")

    @app.route("/miyagi-bot", methods=["POST"])
    def miyagi_bot():
        # """ This route renders hello world """
        command_text = request.data.get("text")
        command_text = command_text.split(" ")
        slack_uid = request.data.get("user_id")
        slackhelper = SlackHelper()
        slack_user_info = slackhelper.user_info(slack_uid)
        actions = Actions(slackhelper, slack_user_info)


        if command_text[0] not in allowed_commands:
            response_body = {"text": "Invalid Command Sent - `/miyagi help` for available commands"}

        if not command_text[0]:
            response_body = actions.welcome()

        if command_text[0] == "write":
            response_body = actions.update_sheet()

        if command_text[0] == "help":
            response_body = actions.help()

        if command_text[0] in ["my-task", "my-tasks"]:
            response_body = actions.my_tasks()

        if command_text[0] in ["show-task", "show-tasks"]:
            date = command_text[1]
            response_body = actions.show_tasks(date)

        response = jsonify(response_body)
        response.status_code = 200
        return response

        
    return app
