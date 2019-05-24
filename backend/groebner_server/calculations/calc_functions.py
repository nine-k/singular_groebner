import os
import subprocess

import logging

import re
import calculations.utils as utils

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

def insert_multiplication(ideals, variables):
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
        parsed_ideal += ideal[prev_end:]
        logger.debug('ideal was %s now is %s' % (ideal, parsed_ideal))
        parsed_ideals.append(parsed_ideal)
    return parsed_ideals


# Generates code to be ran in Singular for the commutative case
def generate_singular_commut(char, variables, ideal, hilbert=False, order_type='dp'):
    ring_decl = "ring r = %d, (%s), %s;" % (char, ','.join(variables), order_type)
    ideal_decl = "ideal i = %s;" % (','.join(new_ideal))
    if not hilbert:
        groebner_decl = "i = groebner(i); i;"
    else:
        groebner_decl = "i = groebner(i); i; hilb(i);"
    inputs = "%s%s%s" % (ring_decl, ideal_decl, groebner_decl)
    return inputs


# Parse the output of singular for the commutative case
def parse_singular_commut(data, hilbert=False):
    gb = list(filter(lambda x: len(x) > 0 and x[:2] == 'i[', data))
    gb = list(map(lambda x: x[1:], gb))

    hs = None
    if hilbert:
        hs = list(filter(lambda x: len(x) > 0 and x[0] == '/' or len(x) == 0, data))
        stop_pos = hs.index('')
        hs = hs[:stop_pos]
    return gb, hs

def get_groebner_basis_commut(char, variables, ideal, hilbert=False, order_type='dp'):
    new_ideal = power_to_multiplication(ideal, variables)
    new_ideal = insert_multiplication(new_ideal, variables)

    inputs = generate_singular_commut(char, variables, new_ideal, hilbert, order_type)
    result = subprocess.run('time Singular',  preexec_fn=utils.limit_fn, shell=True,
                            stderr=subprocess.PIPE, stdout=subprocess.PIPE, input=str.encode(inputs))

    time = str(result.stderr.decode('utf-8')).split(' ')[1]
    outputs = result.stdout.decode('utf-8').split('\n')
    gb, hs = parse_singular_commut(data, hilbert)

    return gb, hs, inputs.replace(';', ';<br>'), time


def parse_singular_noncommut(data, hilbert=False):
    hs = None
    hs_regex = re.compile(r'^\[2\]')
    if hilbert:
        for i in range(len(data)):
            if hs_regex.match(data[i]):
                hs = [data[i + 1]]
                data = data[i + 2:]
                break
    gb = []
    gb_regex = re.compile(r'^\[[0-9]+\]')
    for i in range(len(data)):
        if gb_regex.match(data[i]):
            gb.append(data[i + 1])
    gb = list(map(str.strip, gb))
    return gb, hs

def generate_singular_noncommut(char, variables, ideal, order_type='dp', max_order=4, hilbert=False):
    inputs = 'LIB "fpadim.lib";'
    inputs += "ring r = %d, (%s), %s;" % (char, ','.join(variables), order_type) #ring_decl
    inputs += "int d = %d;" % (max_order) #deg_bound
    inputs += "def R = makeLetterplaceRing(d);" #def_ringR
    inputs += "setring R;" #set_ringR
    inputs += "ideal i = %s;" % (','.join(ideal)) #ideal_decl
    inputs += "ideal J = letplaceGBasis(i);" #ideal_letplace
    if hilbert:
        inputs += "lpDHilbert(J);" #calculate hlbert series
    inputs += "lp2lstr(J, r); setring r; lst2str(@LN, 1);" #convert_to_strings
    return inputs


def get_groebner_basis_noncommut(char, variables, ideal, order_type='dp', max_order=4, hilbert=False):
    hs = None
    new_ideal = power_to_multiplication(ideal, variables)
    new_ideal = insert_multiplication(new_ideal, variables)
    new_ideal = convert_to_letterplace(new_ideal, variables)
    inputs = generate_singular_noncommut(char, variables, new_ideal, order_type, max_order, hilbert)
    result = subprocess.run('time Singular',  preexec_fn=utils.limit_fn, shell=True,
                            stderr=subprocess.PIPE, stdout=subprocess.PIPE, input=str.encode(inputs))
    outputs = result.stdout.decode('utf-8').split('\n')
    time = str(result.stderr.decode('utf-8')).split(' ')[1]
    gb, hs = parse_singular_noncommut(outputs, hilbert)

    return gb, hs, inputs.replace(';', ';<br>'), time



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
