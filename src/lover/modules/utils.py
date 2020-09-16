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
    parameters = '&'.join([str(k) + '=' + str(v) for k, v in args.items()])
    return parameters


def get_parsed_parameters(parser):
    parser.add_argument('id',
                        type=str,
                        help='Inform your profile id to search lovers for you')
    parser.add_argument('start',
                        type=int,
                        help='Inform which number page start')
    parser.add_argument('limit',
                        type=int,
                        help='Inform limit')
    return parser.parse_args()