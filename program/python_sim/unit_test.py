import unittest
from joystick_app import JoystickApp

class TestGetCombinationText(unittest.TestCase):
    def setUp(self):
        self.joystick_app = JoystickApp()
        self.joystick_app.bindings_standard =  {
                1: ['f', 's', 'a'],
                2: ['1', 'f', 'w'],
                3: ['0', '1'],
                4: ['5', '4', 't', 'r', '1'],
                5: []
            }
        

    def test_get_combination_text_up(self):
        self.assertEqual(self.joystick_app.get_combination_text(1), "f+s+a")

    def test_get_combination_text_down(self):
        self.assertEqual(self.joystick_app.get_combination_text(2), "1+f+w")

    def test_get_combination_text_left(self):
        self.assertEqual(self.joystick_app.get_combination_text(3), "0+1")

    def test_get_combination_text_right(self):
        self.assertEqual(self.joystick_app.get_combination_text(4), "5+4+t+r+1")

    def test_get_combination_text_fire(self):
        self.assertEqual(self.joystick_app.get_combination_text(5), "None")


if __name__ == "__main__":
    unittest.main()