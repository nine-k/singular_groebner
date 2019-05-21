import os
import subprocess

import logging

import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def insert_multiplication(ideals, variables):
    def is_operation(x):
        return x in ['-', '*', '+', '^']

    sorted_vars = sorted(variables, key=lambda x: -len(x))
    new_ideals = []
    for ideal in ideals:
        cur_pos = 0
        var_pos = []
        variable_found = True
        while variable_found:
            variable_found = False
            best_varpos = (len(ideal), None)
            logger.debug("left to parse: %s" % ideal[cur_pos:])
            for num, var in enumerate(sorted_vars):
                curvar_pos = ideal[cur_pos:].find(var)
                if (curvar_pos != -1):
                    curvar_pos += cur_pos
                    if (curvar_pos < best_varpos[0]):
                        best_varpos = (curvar_pos, num)
                        variable_found = True
            if (variable_found):
                cur_pos = best_varpos[0] + len(sorted_vars[best_varpos[1]])
                logger.debug("found variable %s at %d" % (sorted_vars[best_varpos[1]], best_varpos[0]))
                var_pos.append(best_varpos)
        new_ideal = ""
        prev_end = 0
        logger.debug(var_pos)
        for i in range(len(var_pos) - 1):
            pos, var = var_pos[i]
            pos_next, var_next = var_pos[i + 1]
            new_ideal += ideal[prev_end: pos + len(sorted_vars[var])]
            if (pos + len(sorted_vars[var]) == pos_next):
                new_ideal += '*'
            prev_end = pos + len(sorted_vars[var])
        new_ideal += ideal[prev_end:]
        logger.debug('ideal was %s now is %s' % (ideal, new_ideal))
        new_ideals.append(new_ideal)
    return new_ideals


def convert_to_letterplace(ideals, variables):
    ideal_letplace = []
    for ideal in ideals:
        res = ''
        ideal += '+'
        prev_i = 0
        for i in range(len(ideal)):
            if ideal[i] in ('+', '-'):
                poly = list(map(str.strip, ideal[prev_i:i].split('*')))
                cnt = 1
                for j, elem in enumerate(poly):
                    res += elem
                    if elem in variables:
                        res += '(' + str(cnt) + ')'
                        cnt += 1
                    if j != len(poly) - 1:
                        res += '*'
                prev_i = i + 1
                res = res + ideal[i]
        ideal_letplace += [res[:-1]]
    return ideal_letplace

def power_to_multiplication(ideals, variables):
    variables.sort(key=len, reverse=True)
    regexp = re.compile('|'.join(
        map(
            lambda x: x + '\^[0-9]+',
            variables
        )))
    parsed_ideals = []
    prev_end = 0
    for ideal in ideals:
        parsed_ideal = ''
        matches = list(regexp.finditer(ideal))
        if len(matches) == 0:
            logger.debug('ideal was %s. nothing to change here' % (ideal))
            parsed_ideals.append(ideal)
            continue

        for match in matches:
            parsed_ideal += ideal[prev_end:match.start()]
            var = match.group()[:match.group().find('^')]
            power = int(match.group()[match.group().find('^') + 1:])
            logger.debug("in monom %s var is %s pow is %s" % (match.group(), var, power))
            parsed_ideal += (var + '*') * (power - 1) + var
            prev_end = match.end()
        logger.debug('ideal was %s now is %s' % (ideal, parsed_ideal))
        parsed_ideals.append(parsed_ideal)
    return parsed_ideals


def get_groebner_basis_commut(char, variables, ideal, order_type='dp'):
    #inputs = open(file_name, 'w')
    ring_decl = "ring r = %d, (%s), %s;" % (char, ','.join(variables), order_type)
    ideal_decl = "ideal i = %s;" % (','.join(ideal))
    groebner_decl = "groebner(i);"
    inputs = "%s%s%s" % (ring_decl, ideal_decl, groebner_decl)
    result = subprocess.run('Singular', stdout=subprocess.PIPE, input=str.encode(inputs))
    outputs = result.stdout.decode('utf-8').split('\n')
    outputs = list(filter(lambda x: len(x) > 0 and x[0] == '_', outputs))
    return outputs

def get_groebner_basis_noncommut(char, variables, ideal, order_type='dp', max_order=4, hilbert=False):
    inputs = ""
    inputs += 'LIB "freegb.lib";' #lib
    inputs += "ring r = %d, (%s), %s;" % (char, ','.join(variables), order_type) #ring_decl
    inputs += "int d = %d;" % (max_order) #deg_bound
    inputs += "def R = makeLetterplaceRing(d);" #def_ringR
    inputs += "setring R;" #set_ringR
    new_ideal = insert_multiplication(ideal, variables)
    new_ideal = convert_to_letterplace(power_to_multiplication(new_ideal, variables), variables)
    inputs += "ideal i = %s;" % (','.join(new_ideal)) #ideal_decl
    inputs += "option(redSB); option(redTail);" #options
    inputs += "ideal J = letplaceGBasis(i);" #ideal_letplace
    inputs += "lp2lstr(J, r); setring r; lst2str(@LN, 1);" #convert_to_strings
    logger.debug(';\n'.join(inputs.split(';')))
    result = subprocess.run('Singular', stdout=subprocess.PIPE, input=str.encode(inputs))
    outputs = result.stdout.decode('utf-8').split('\n')
    gb = []
    for i in range(len(outputs)):
        if outputs[i][-2:] == ']:':
            gb.append(outputs[i + 1])
    gb = list(map(str.strip, gb))
    if not hilbert:
        return gb
    inputs = 'LIB "fpadim.lib";'
    inputs += "ring r = %d, (%s), %s;" % (char, ','.join(variables), order_type) #ring_decl
    inputs += "int d = %d;" % (max_order) #deg_bound
    inputs += "def R = makeLetterplaceRing(d);" #def_ringR
    inputs += "setring R;" #set_ringR
    inputs += "ideal i = %s;" % (','.join(new_ideal)) #ideal_decl
    inputs += "ideal J = letplaceGBasis(i);" #ideal_letplace
    inputs += "lpDHilbert(J);" #calculate hlbert series
    result = subprocess.run('Singular', stdout=subprocess.PIPE, input=str.encode(inputs))
    hs = result.stdout.decode('utf-8').split('\n')[-4: -1]
    logger.debug(hs)
    return gb, hs



if __name__ == '__main__':
    print(get_groebner_basis_commut(
                                    0,
                                    ['a', 'b', 'c', 'd'],
                                    'a+b+c+d,a*b+a*d+b*c+c*d,a*b*c+a*b*d+a*c*d+b*c*d,a*b*c*d-1'.split(',')
                                   ))
    print(get_groebner_basis_noncommut(
                                    0,
                                    ['a', 'b', 'c', 'd'],
                                    'a+b+c+d,a*b+a*d+b*c+c*d,a*b*c+a*b*d+a*c*d+b*c*d,a*b*c*d-1'.split(',')
                                   ))
