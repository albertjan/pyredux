from __future__ import absolute_import, unicode_literals
import unittest
import inspect

from pyrsistent import pmap
from ..Reducer import combine_reducer


def a_reducer(state, action):
    return state.update({"actionA": action})


def b_reducer(state, action):
    return state.update({"actionB": action})


class ReducerKlass(object):
    def c_reducer(self, state, action):
        return state.update({"actionC": action})


def e_reducer(state, action):
    if action.type == "do":
        return state.update({"actionE": action})
    else:
        return state


def d_reducer(state, action):
    if action.type == "do_it":
        return state.update({"actionE": action})
    else:
        return state


class ActionMock(object):
    def __init__(self, type_):
        self.type = type_


class TestCombineReducer(unittest.TestCase):
    def test_combine_reducer_returns_function(self):
        combined = combine_reducer([a_reducer, b_reducer])
        self.assertTrue(
            inspect.isfunction(combined),
            "combine_reducer does not return a function"
        )

    def test_combine_reducer_will_make_subtree_states_by_function_name(self):
        combined = combine_reducer([a_reducer, b_reducer])
        initial_state = combined(action="asdf")
        self.assertItemsEqual(["a_reducer", "b_reducer"], initial_state.keys())

    def test_combine_reducer_will_make_subtree_states_by_method_name(self):
        combined = combine_reducer([a_reducer, ReducerKlass().c_reducer])
        initial_state = combined(action="zz!!")
        self.assertItemsEqual(["a_reducer", "c_reducer"], initial_state.keys())

    def test_state_split_keys_can_be_changed_through_dict(self):
        combined = combine_reducer({"a": a_reducer, "b": b_reducer})
        initial_state = combined(action={"unittest": "ignore"})
        self.assertEqual(["a", "b"], initial_state.keys())

    def test_combine_reducer_will_split_the_state_tree_in_sections_per_reducer_single(self):
        combined = combine_reducer([a_reducer])
        action_obj = "unittest"
        expected_state = pmap({
            "a_reducer": pmap(
                {"actionA": action_obj})
        })
        actual_state = combined(action=action_obj)
        self.assertEqual(expected_state, actual_state)

    def test_combine_reducer_create_one_part_tree_per_reducer(self):
        reducer_list = [a_reducer, b_reducer]
        combined = combine_reducer(reducer_list)
        action_obj = {"2": 3}
        actual_state = combined(action=action_obj)
        expected_state = pmap(
            {"a_reducer": {"actionA": action_obj},
             "b_reducer": {"actionB": action_obj}
             }
        )
        self.assertEqual(expected_state, actual_state)

    def test_combined_reducer_will_not_change_the_state_if_nothing_to_do(self):
        action = ActionMock("ignore_action")
        combined = combine_reducer([e_reducer, d_reducer])
        initial_state = combined(action=action)
        untransformed_state = combined(initial_state, action)
        self.assertTrue(
            initial_state is untransformed_state,
            "State object has not the same reference! It must be updated!"
        )

    def test_combined_reducer_returns_new_state_object_when_one_part_tree_changes(self):
        initial_action = ActionMock("ignore_action")
        action = ActionMock("do")
        combined = combine_reducer([e_reducer, d_reducer])
        initial_state = combined(action=initial_action)
        transformed_state = combined(initial_state, action)
        self.assertTrue(
            initial_state is not transformed_state,
            "State object has not the same reference! It must be updated!"
        )