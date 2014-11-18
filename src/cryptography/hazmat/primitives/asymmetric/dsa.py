# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

import six

from cryptography import utils


def generate_parameters(key_size, backend):
    return backend.generate_dsa_parameters(key_size)


def generate_private_key(key_size, backend):
    return backend.generate_dsa_private_key_and_parameters(key_size)


def _check_dsa_parameters(parameters):
    if utils.bit_length(parameters.p) not in [1024, 2048, 3072]:
        raise ValueError("p must be exactly 1024, 2048, or 3072 bits long")
    if utils.bit_length(parameters.q) not in [160, 256]:
        raise ValueError("q must be exactly 160 or 256 bits long")

    if not (1 < parameters.g < parameters.p):
        raise ValueError("g, p don't satisfy 1 < g < p.")


def _check_dsa_private_numbers(numbers):
    parameters = numbers.public_numbers.parameter_numbers
    _check_dsa_parameters(parameters)
    if numbers.x <= 0 or numbers.x >= parameters.q:
        raise ValueError("x must be > 0 and < q.")

    if numbers.public_numbers.y != pow(parameters.g, numbers.x, parameters.p):
        raise ValueError("y must be equal to (g ** x % p).")


class DSAParameterNumbers(object):
    def __init__(self, p, q, g):
        if (
            not isinstance(p, six.integer_types) or
            not isinstance(q, six.integer_types) or
            not isinstance(g, six.integer_types)
        ):
            raise TypeError(
                "DSAParameterNumbers p, q, and g arguments must be integers."
            )

        self._p = p
        self._q = q
        self._g = g

    p = utils.read_only_property("_p")
    q = utils.read_only_property("_q")
    g = utils.read_only_property("_g")

    def parameters(self, backend):
        return backend.load_dsa_parameter_numbers(self)


class DSAPublicNumbers(object):
    def __init__(self, y, parameter_numbers):
        if not isinstance(y, six.integer_types):
            raise TypeError("DSAPublicNumbers y argument must be an integer.")

        if not isinstance(parameter_numbers, DSAParameterNumbers):
            raise TypeError(
                "parameter_numbers must be a DSAParameterNumbers instance."
            )

        self._y = y
        self._parameter_numbers = parameter_numbers

    y = utils.read_only_property("_y")
    parameter_numbers = utils.read_only_property("_parameter_numbers")

    def public_key(self, backend):
        return backend.load_dsa_public_numbers(self)


class DSAPrivateNumbers(object):
    def __init__(self, x, public_numbers):
        if not isinstance(x, six.integer_types):
            raise TypeError("DSAPrivateNumbers x argument must be an integer.")

        if not isinstance(public_numbers, DSAPublicNumbers):
            raise TypeError(
                "public_numbers must be a DSAPublicNumbers instance."
            )
        self._public_numbers = public_numbers
        self._x = x

    x = utils.read_only_property("_x")
    public_numbers = utils.read_only_property("_public_numbers")

    def private_key(self, backend):
        return backend.load_dsa_private_numbers(self)