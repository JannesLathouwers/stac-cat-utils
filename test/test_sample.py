from unittest import TestCase


class TestSample(TestCase):

    def test_string_equality(self):
        self.assertEqual('test', 'test')
