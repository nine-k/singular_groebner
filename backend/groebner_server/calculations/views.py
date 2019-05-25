from django.http import HttpResponse
from django.core.mail import send_mail
import json

import pipes
import calculations.calc_functions as calcs
import calculations.utils as utils
from celery import task

import logging
import sys

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def index(request):
    return HttpResponse("Hello, world.")


@task
def do_calculation(data):
    data['characteristic'] = int(data['characteristic'])
    data['vars'] = list(filter(
                        lambda x: x != '',
                        map(
                            lambda x: x.replace(' ', '').strip(),
                            # data['vars'].split(';')
                            utils.SEPARATOR_REGEX.split(data['vars'])
                           )
                       ))
    data['basis'] = list(filter(
                         lambda x: x != '',
                         map(
                             lambda x: x.replace(' ', '').strip(),
                             # data['basis'].split(';')
                             utils.SEPARATOR_REGEX.split(data['basis'])
                            )
                        ))
    data['hilbert'] = (data['hilbert'] == 1)
    logger.debug(data)
    calc_res = calcs.get_groebner_basis[(data['request'], data['platform'])](data['characteristic'],
                                                                             data['vars'],
                                                                             data['basis'],
                                                                             hilbert=data['hilbert'],
                                                                             max_order=int(data['max_degree']))

    response = dict()
    response['basis'] = '<br>'.join(calc_res[0][:utils.MAX_BASIS_LINES])
    response['code'] = calc_res[2]
    response['time'] = calc_res[3]
    response['hilbert'] = ''
    if data['hilbert']:
        response['hilbert'] = '<br>'.join(calc_res[1])

    if not data['hilbert']:
        calc_res = '\n'.join(calc_res[0])
    else:
        calc_res = 'Groebner basis:\n' + '\n'.join(calc_res[0]) + '\nHilbert series\n' + '\n'.join(calc_res[1])
    if data['email']:
        send_mail('groebner basis calculation results',\
                  calc_res,
                  'groebner@calc.edu',
                  [data['email']])
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
        except:
            logger.debug('exception cought')
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
