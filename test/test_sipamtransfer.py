import unittest
import main


class TestTransfer(unittest.TestCase):

    def test_xml_to_json(self):
        result = ''.join(main.xml_to_json('dc.xml').split())

        expected = ''.join('{"title": "Test Title",'
                           '"identifier": "Test ID",'
                           '"creator": "Test Creator",'
                           '"date": "Test Date"}'.split())

        self.assertEqual(result, expected)

    def test_validate_directories(self):
        invalid_sip = main.validate_directories('incorrect123', '..')
        self.assertEqual(invalid_sip, False, 'Invalid sip directory accepted.')

        invalid_output = main.validate_directories('..', 'incorrect123')
        self.assertEqual(invalid_output, False, 'Invalid output directory accepted.')

        valid_sip_output = main.validate_directories('..', '..')
        self.assertEqual(valid_sip_output, True, "Valid input not accepted")
