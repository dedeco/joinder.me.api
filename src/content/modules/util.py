from flask import request
from marshmallow import ValidationError


def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')


def min_length(length):
    def validate(s):
        if len(s) >= length:
            return s
        raise ValidationError("String must be at least %i characters long" % min)

    return validate


def get_parsed_parameters(parser):
    parser. \
        add_argument('lookup',
                     type=min_length(3),
                     required=True,
                     help='The partial query for cities name typed by the user, e.g. bel. Submitted parameter '
                          'must not be under 3 chars.')
    args = parser.parse_args()
    return args
