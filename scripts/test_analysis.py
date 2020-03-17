#!/usr/bin/python3

import unittest
from analyze_report import *


class TestAnalyzeDstat(unittest.TestCase):
    def test_get_container_settings_from_test_name(self):
        valid_data = {
            'official_5mp': {
                'test_plan': 'official',
                'mp': 5,
                'mrpp': 1000,
                'cores': 2
            },
            'extreme_4core_10mp': {
                'test_plan': 'extreme',
                'mp': 10,
                'mrpp': 1000,
                'cores': 4
            },
        '1200_1000mp_4core': {
            'test_plan': '1200',
            'mp': 1000,
            'mrpp': 1000,
            'cores': 4
        },
            'extreme': {
                'test_plan': 'extreme',
                'mp': 5,
                'mrpp': 1000,
                'cores': 2
            },
            'extreme_4core_10mp_1500mrpp': {
                'test_plan': 'extreme',
                'mp': 10,
                'mrpp': 1500,
                'cores': 4
            }
        }
        for test in valid_data:
            data = get_container_settings_from_test_name(test)
            for key in data:
                assert data[key] == valid_data[test][key]


if __name__ == "__main__":
    unittest.main()
