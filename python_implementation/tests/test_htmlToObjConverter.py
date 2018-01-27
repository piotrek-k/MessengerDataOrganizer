from htmlToObjConverter import string_date_to_object_date_converter
import unittest
import datetime
import pytz

class DataConverterTest(unittest.TestCase):
    def test_converting_string_time(self):
        date_as_string = "Sunday, January 4, 2015 at 4:03pm UTC+01"

        generated_time = string_date_to_object_date_converter(date_as_string)
        proper_time = datetime.datetime(2015, 1, 4, 16, 3, 0, tzinfo=pytz.timezone("CET"))

        self.assertEqual(proper_time, generated_time)