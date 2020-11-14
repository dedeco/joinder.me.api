def get_paginated_list(schema, results, url, parameters, start, limit):
    start = int(start)
    limit = int(limit)
    count = len(results)

    obj = {'start': start, 'limit': limit, 'count': count}

    if count < start or limit < 0:
        obj['results'] = []
        return obj
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + \
                          '?start=%d&limit=%d' % (start_copy, limit_copy) \
                          + '&' + parameters
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + \
                      '?start=%d&limit=%d' % (start_copy, limit) \
                      + '&' + parameters
    obj['results'] = schema.dump(results[(start - 1):(start - 1 + limit)])
    return obj


def get_parameters_url(args):
    parameters = '&'.join([str(k) + '=' + str(v) for k, v in args.items() if k not in ["start", "limit"]])
    return parameters


def get_parsed_parameters_for_deck(parser):
    parser.add_argument('id',
                        type=str,
                        help='Inform your profile id to search lovers for you')
    parser.add_argument('start',
                        type=int,
                        help='Inform start element to pagination')
    parser.add_argument('limit',
                        type=int,
                        help='Inform quantity of element per page')
    return parser.parse_args()


def get_parsed_parameters(parser):
    parser.add_argument('match_id',
                        type=str,
                        help='Inform your profile match id to get details ')
    return parser.parse_args()
