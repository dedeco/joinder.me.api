import requests

from flask import current_app, render_template
from jinja2 import FileSystemLoader, Environment

from src.task.models.email_type import EmailType


def get_parsed_parameters(parser):
    parser.add_argument('identifier',
                        type=str,
                        help='Get user_service by identifier')
    parser.add_argument('uid',
                        type=str,
                        help='Get user_service by uid')
    parser.add_argument('cache',
                        type=str,
                        help='Avoid cache when received something here')
    return parser.parse_args()


def get_parsed_parameters_firebase(parser):
    parser.add_argument('email',
                        type=EmailType('RFC5322'),
                        required=True,
                        help='Please, inform user email')
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help='Please, inform user password')
    parser.add_argument('display_name',
                        type=str,
                        required=True,
                        help='Please, inform display name')
    return parser.parse_args()


def send_message_confirm_email(name, email, link):
    return requests.post(
        current_app.config.get("MAILGUM_BASE_URL"),
        auth=("api", current_app.config.get("MAILGUM_API_KEY")),
        data={"from": "No reply <no-reply@emails.joinder.me>",
              "to": [name, email],
              "subject": "Confirm your email",
              "text": "Click here to confirm {}".format(link),
              "html": generate_html(link, 'en_US_confirm.html')}
    )


def send_message_reset_password(name, email, link):
    return requests.post(
        current_app.config.get("MAILGUM_BASE_URL"),
        auth=("api", current_app.config.get("MAILGUM_API_KEY")),
        data={"from": "No reply <no-reply@emails.joinder.me>",
              "to": [name, email],
              "subject": "Reset your password",
              "text": "Click here to reset {}".format(link),
              "html": generate_html(link, 'en_US_recovery.html')}
    )


def send_message_report_bad_behavior(name, email, type_reason, message):
    return requests.post(
        current_app.config.get("MAILGUM_BASE_URL"),
        auth=("api", current_app.config.get("MAILGUM_API_KEY")),
        data={"from": "No reply <no-reply@emails.joinder.me>",
              "to": [name, email],
              "subject":"DENÚNCIA JOINDER.ME",
              "text": "DENÚNCIA JOINDER.ME",
              "html": generate_html_report(type_reason, message, 'en_US_report.html')}
    )


def generate_html(link, type_):
    return Environment(
        loader=FileSystemLoader('src/user/modules/templates')
    ).get_template(type_).render(link=link)


def generate_html_report(type_reason, message, type_):
    return Environment(
        loader=FileSystemLoader('src/user/modules/templates')
    ).get_template(type_).render(type_reason=type_reason, message=message)
