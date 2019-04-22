from django.http import HttpResponse
from django.core.mail import send_mail
import json

import pipes
import calculations.calc_functions as calcs

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
        data['vars'] = list(filter(lambda x: x != '', map(str.strip, data['vars'].split(';'))))
        data['basis'] = list(filter(lambda x: x != '', map(str.strip, data['basis'].split(';'))))
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
            calc_res = '\n'.join(calcs.get_groebner_basis_noncommut(data['characteristic'], data['vars'], data['basis']))
                                                                     #data['max_order']))
        send_mail('groebner basis calculation results',\
                  calc_res,
                  'groebner@calc.edu',
                  [data['email']])


    return HttpResponse("Hello, world.")
