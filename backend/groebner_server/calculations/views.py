from django.http import HttpResponse
from django.core.mail import EmailMessage
import json

import pipes
import calculations.calc_functions as calcs
import calculations.utils as utils

import logging
import sys

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def index(request):
    return HttpResponse("Hello, world.")


def do_calculation(data):
    data['characteristic'] = int(data['characteristic'])
    data['vars'] = list(filter(
                        lambda x: x != '',
                        map(
                            lambda x: x.replace(' ', '').strip(),
                            # data['vars'].split(';')
                            utils.VAR_SEPARATOR_REGEX.split(data['vars'])
                           )
                       ))
    data['basis'] = list(filter(
                         lambda x: x != '',
                         map(
                             lambda x: x.replace(' ', '').strip(),
                             # data['basis'].split(';')
                             utils.IDEAL_SEPARATOR_REGEX.split(data['basis'])
                            )
                        ))
    data['hilbert'] = (data['hilbert'] == 1)
    logger.debug(data)
    calc_res = calcs.get_groebner_basis[(data['request'], data['platform'])](data['characteristic'],
                                                                             data['vars'],
                                                                             data['basis'],
                                                                             hilbert=data['hilbert'],
                                                                             max_order=int(data['max_degree']))

    logger.debug(calc_res)
    response = dict()
    response['basis'] = '<br>'.join(calc_res[0][:utils.MAX_BASIS_LINES])
    response['code'] = calc_res[2]
    response['time'] = calc_res[3]
    response['hilbert'] = ''
    if data['hilbert']:
        response['hilbert'] = '<br>'.join(calc_res[1])

    if data['email']:
        message = EmailMessage('groebner basis calculation results',
                               'code\n%s' % calc_res[2].replace('<br>', '\n'),
                               'groebner@calc.edu',
                               [data['email']])
        message.attach('groebner.txt', '\n'.join(calc_res[0]), 'text/plain')
        if data['hilbert']:
            message.attach('hilbert.txt', '\n'.join(calc_res[1]), 'text/plain')
        message.send()
    return response

def submit_calculation(request):
    if request.method == 'POST' and request.content_type == 'application/json': #probably received a calculation to be done
        data = json.loads(request.body)
        if not utils.check_content(data):
            response = HttpResponse()
            response.status_code = 404
            return response
        calculation_results = do_calculation(data)
        '''
        try:
            calculation_results = do_calculation(data)
        except Exception as err:
            logger.debug('exception cought %s' % err)
            response = HttpResponse()
            response.status_code = 500
            return response
        '''
        response = HttpResponse(json.dumps(calculation_results).encode('utf-8'))
        response.status_code = 200
        response['Access-Control-Allow-Origin'] = '165.22.70.250:80'
        return response

    response = HttpResponse()
    response.status_code = 404
    return response
