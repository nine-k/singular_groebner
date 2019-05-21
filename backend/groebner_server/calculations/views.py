from django.http import HttpResponse
from django.core.mail import send_mail
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

def submit_calculation(request):
    if request.method == 'POST' and request.content_type == 'application/json': #probably received a calculation to be done
        data = json.loads(request.body)
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
        data['max_degree'] = int(data['max_degree'])
        data['hilbert'] = (data['hilbert'] == 1)
        logger.debug(data)
        calc_res = ''
        if data['request'] == 'commutative_groebner':
            logger.debug('calcing commutative groebner')
            calc_res = '\n'.join(
                    calcs.get_groebner_basis_commut(
                        data['characteristic'],
                        data['vars'],
                        data['basis']
                        )
                    )
        elif data['request'] == 'noncommutative_groebner':
            logger.debug('calcing noncommutative groebner')
            #data['max_order'] = int(data['max_order'])
        calc_res = calcs.get_groebner_basis_noncommut(data['characteristic'],
                                                                    data['vars'], data['basis'],
                                                                    max_order=data['max_degree'],
                                                                    hilbert=(data['hilbert'] == 1))
        response = HttpResponse()
        response['basis'] = '<br>'.join(calc_res[0][:utils.MAX_BASIS_LINES])
        if data['hilbert']:
            response['hilbert'] = '<br>'.join(calc_res[1])

        if not data['hilbert']:
            calc_res = '\n'.join(calc_res)
        else:
            calc_res = 'Groebner basis:\n' + '\n'.join(calc_res[0]) + '\nHilbert series\n' + '\n'.join(calc_res[1])
        if data['email']:
            send_mail('groebner basis calculation results',\
                      calc_res,
                      'groebner@calc.edu',
                      [data['email']])
    return response
