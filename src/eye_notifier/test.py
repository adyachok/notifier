import mock
import unittest

import eye_notify

eye_notify.check_existence = mock.Mock(return_value=True)
eye_notify.Player = mock.MagicMock()
eye_notify.Timer = mock.Mock()

from unittest import TestCase
from eye_notify import Engine, WaitingState, WorkState, RelaxState


class TestEyeNotifier(TestCase):
    """
    This test class maid to test State machine states switching
    in class Engine and method process event.
    """

    def setUp(self):
        self.engine = Engine()

    def test_state_switch(self):
        self.engine.process_event(empty=True)
        self.assertTrue(isinstance(self.engine.state, RelaxState),
                        'The state is %s' % self.engine.state)

    def test_switch_too_waiting(self):
        self.engine.process_event(elapsed=5)
        self.assertTrue(isinstance(self.engine.state, WaitingState))
        prev_state = self.engine.state.waiting_state
        self.assertTrue(isinstance(prev_state, WorkState),
                        'The state is %s' % prev_state)
        self.assertEqual(prev_state.elapsed, 5)

    def test_check_right_elapsed_count(self):
        self.engine.process_event(elapsed=5)
        self.engine.process_event(elapsed=5)
        self.engine.process_event(elapsed=5)
        self.engine.process_event(elapsed=5)
        self.assertEqual(self.engine.state.elapsed, 10)
        self.assertTrue(isinstance(self.engine.state, WorkState),
                        'The state is %s' % self.engine.state)

    def test_check_over_elapsed_count(self):
        self.engine.process_event(elapsed=2400)
        self.assertEqual(self.engine.state.waiting_state.elapsed, 2400)
        self.engine.process_event(elapsed=300)
        self.engine.process_event(elapsed=300)
        self.engine.process_event(elapsed=300)
        self.assertEqual(self.engine.state.elapsed, 2700)
        self.assertEqual(self.engine.state.get_timeout(), 0)

    def test_trigger_new_state(self):
        self.engine.process_event(empty=True)
        self.assertTrue(isinstance(self.engine.state, RelaxState))

    def assert_trigger_new_state_2(self):
        self.engine.process_event(elapsed=5)
        self.assertTrue(isinstance(self.engine.state, WaitingState))
        self.engine.process_event(elapsed=5)
        self.engine.process_event(empty=True)
        self.assertTrue(isinstance(self.engine.state, RelaxState))

    def test_switch_overtime_relax_state(self):
        self.engine.process_event(empty=True)
        self.engine.process_event(elapsed=300)
        self.assertTrue(isinstance(self.engine.state.waiting_state, RelaxState),
                        'The state is %s' % self.engine.state)
        self.engine.process_event(elapsed=1500)
        self.assertTrue(isinstance(self.engine.state, WorkState),
                        'The state is %s' % self.engine.state)



if __name__ == "__main__":
     unittest.main()