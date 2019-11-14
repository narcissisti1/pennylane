# Copyright 2018 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Tests for the templates utility functions.
"""
# pylint: disable=protected-access,cell-var-from-loop
import pytest
import numpy as np
from pennylane.qnode import Variable
from pennylane.templates.utils import (_check_wires,
                                       _check_shape,
                                       _check_shapes,
                                       _get_shape,
                                       _check_number_of_layers,
                                       _check_no_variable,
                                       _check_hyperp_is_in_options,
                                       _check_type)


#########################################
# Inputs

WIRES_PASS = [(0, ([0], 1)),
              ([4], ([4], 1)),
              ([1, 2], ([1, 2], 2))]
WIRES_FAIL = [[-1],
              ['a'],
              lambda x: x]

SHAPE_PASS = [(0.231, (), None),
              ([[1., 2.], [3., 4.]], (2, 2), None),
              ([-2.3], (1, ), None),
              ([-2.3, 3.4], (4,), 'max'),
              ([-2.3, 3.4], (1,), 'min'),
              ([-2.3], (1,), 'max'),
              ([-2.3], (1,), 'min'),
              ([[-2.3, 3.4], [1., 0.2]], (3, 3), 'max'),
              ([[-2.3, 3.4, 1.], [1., 0.2, 1.]], (1, 2), 'min'),
              ]

SHAPE_LST_PASS = [([0.231, 0.1], [(), ()], None),
                  ([[1., 2.], [4.]], [(2, ), (1, )], None),
                  ([[-2.3], -1.], [(1, ), ()], None),
                  ([[-2.3, 0.1], -1.], [(1,), ()], 'min'),
                  ([[-2.3, 0.1], -1.], [(3,), ()], 'max')
                  ]

SHAPE_FAIL = [(0.231, (1,), None),
              ([[1., 2.], [3., 4.]], (2, ), None),
              ([-2.3], (4, 5), None),
              ([-2.3, 3.4], (4,), 'min'),
              ([-2.3, 3.4], (1,), 'max'),
              ([[-2.3, 3.4], [1., 0.2]], (3, 3), 'min'),
              ([[-2.3, 3.4, 1.], [1., 0.2, 1.]], (1, 2), 'max'),
              ]

GET_SHAPE_PASS = [(0.231, ()),
                  ([[1., 2.], [3., 4.]], (2, 2)),
                  ([-2.3], (1, )),
                  ([-2.3, 3.4], (2,)),
                  ([-2.3], (1,)),
                  ([[-2.3, 3.4, 1.], [1., 0.2, 1.]], (2, 3)),
                  ]

GET_SHAPE_FAIL = []

SHAPE_LST_FAIL = [([0.231, 0.1], [(), (3, 4)], None),
                  ([[1., 2.], [4.]], [(1, ), (1, )], None),
                  ([[-2.3], -1.], [(1, 2), (1,)], None),
                  ([[-2.3, 0.1], -1.], [(1,), ()], 'max'),
                  ([[-2.3, 0.1], -1.], [(3,), ()], 'min')
                  ]

LAYERS_PASS = [([[1], [2], [3]], 1),
               ([[[1], [2], [3]], [['a'], ['b'], ['c']]], 3),
             ]

LAYERS_FAIL = [([1, 2, 3], None),
               ([[[1], [2], [3]], [['b'], ['c']]], 3),
              ]

NOVARS_PASS = [[[], np.array([1., 4.])],
               [1, 'a']]

NOVARS_FAIL = [[[Variable(0.1)], Variable([0.1])],
               np.array([Variable(0.3), Variable(4.)]),
               [Variable(-1.)]]

OPTIONS_PASS = [("a", ["a", "b"])]

OPTIONS_FAIL = [("c", ["a", "b"])]

TYPE_PASS = [(["a"], list, type(None)),
             (1, int, type(None)),
             ("a", int, str),
             (Variable(1.), list, Variable)
             ]

TYPE_FAIL = [("a", list, type(None)),
             (Variable(1.), int, list),
             (1., Variable, type(None))
             ]

##############################


class TestInputChecks:
    """Test private functions that check the input of templates."""

    @pytest.mark.parametrize("wires, targt", WIRES_PASS)
    def test_check_wires(self, wires, targt):
        res = _check_wires(wires=wires)
        assert res == targt

    @pytest.mark.parametrize("wires", WIRES_FAIL)
    def test_check_wires_exception(self, wires):
        with pytest.raises(ValueError):
            _check_wires(wires=wires)

    @pytest.mark.parametrize("inpt, target_shape, bound", SHAPE_PASS)
    def test_check_shape(self, inpt, target_shape, bound):
        _check_shape(inpt, target_shape, bound=bound)

    @pytest.mark.parametrize("inpt, target_shape, bound", SHAPE_LST_PASS)
    def test_check_shape_list_of_inputs(self, inpt, target_shape, bound):
        _check_shapes(inpt, target_shape, bound_list=[bound]*len(inpt))

    @pytest.mark.parametrize("inpt, target_shape, bound", SHAPE_FAIL)
    def test_check_shape_exception(self, inpt, target_shape, bound):
        with pytest.raises(ValueError):
            _check_shape(inpt, target_shape, bound=bound)

    @pytest.mark.parametrize("inpt, target_shape, bound", SHAPE_LST_FAIL)
    def test_check_shape_list_of_inputs_exception(self, inpt, target_shape, bound):
        with pytest.raises(ValueError):
            _check_shapes(inpt, target_shape, bound_list=[bound]*len(inpt))

    @pytest.mark.parametrize("inpt, target_shape", GET_SHAPE_PASS)
    def test_get_shape(self, inpt, target_shape):
        shape = _get_shape(inpt)
        assert shape == target_shape

    # @pytest.mark.parametrize("inpt", GET_SHAPE_FAIL)
    # def test_get_shape_exception(self, inpt):
    #     with pytest.raises(ValueError):
    #         _get_shape(inpt)

    @pytest.mark.parametrize("inpt, repeat", LAYERS_PASS)
    def test_check_num_layers(self, inpt, repeat):
        n_layers = _check_number_of_layers(inpt)
        assert n_layers == repeat

    @pytest.mark.parametrize("inpt, repeat", LAYERS_FAIL)
    def test_check_num_layers_exception(self, inpt, repeat):
        with pytest.raises(ValueError):
            _check_number_of_layers(inpt)

    def test_check_shape_exception_message(self):
        with pytest.raises(ValueError) as excinfo:
            _check_shape([0.], (3,), msg="XXX")
        assert "XXX" in str(excinfo.value)

    @pytest.mark.parametrize("arg", NOVARS_PASS)
    def test_check_no_variables(self, arg):
        _check_no_variable(arg, "dummy")

    @pytest.mark.parametrize("arg", NOVARS_FAIL)
    def test_check_no_variables_exception(self, arg):
        with pytest.raises(ValueError):
            _check_no_variable(arg, "dummy")

    def test_check_no_variables_exception_message(self):
        with pytest.raises(ValueError) as excinfo:
            a = Variable(0)
            _check_no_variable([a], ["dummy"], msg="XXX")
        assert "XXX" in str(excinfo.value)

    @pytest.mark.parametrize("hp, opts", OPTIONS_PASS)
    def test_check_hyperp_options(self, hp, opts):
        _check_hyperp_is_in_options(hp, opts)

    @pytest.mark.parametrize("hp, opts", OPTIONS_FAIL)
    def test_check_hyperp_options_exception(self, hp, opts):
        with pytest.raises(ValueError):
            _check_hyperp_is_in_options(hp, opts)

    @pytest.mark.parametrize("hp, typ, alt", TYPE_PASS)
    def test_check_type(self, hp, typ, alt):
        _check_type(hp, [typ, alt])

    @pytest.mark.parametrize("hp, typ, alt", TYPE_FAIL)
    def test_check_type_exception(self, hp, typ, alt):
        with pytest.raises(ValueError):
            _check_type(hp, [typ, alt])

    @pytest.mark.parametrize("hp, typ, alt", TYPE_FAIL)
    def test_check_type_exception_message(self, hp, typ, alt):
        with pytest.raises(ValueError) as excinfo:
            _check_type(hp, [typ, alt], msg="XXX")
        assert "XXX" in str(excinfo.value)
