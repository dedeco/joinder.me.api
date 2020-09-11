from src.task.models.email_type import EmailType


def get_parsed_parameters(parser):
    parser.add_argument('id',
                        type=str,
                        help='Get profile_service by id')

    parser.add_argument('email',
                        type=EmailType('RFC5322'),
                        help='Get profile_service by email')

    if not parser.parse_args().get('email'):
        parser_copy = parser.copy()
        parser_copy.replace_argument('id', required=True, type=str,
                                     help='Get profile_service by id')
        return parser_copy.parse_args()
    return parser.parse_args()
