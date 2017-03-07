from unittest import TestCase
from terraform_validator.validator import ResourceContainer


class TestResourceContainer(TestCase):
    def setUp(self):
        test_dict = {
            'parameter.#': '1',
            'parameter.2943476575.name': 'cluster-enabled',
            'parameter.2943476575.value': 'no',
            'ingress.3133039999.cidr': '0.0.0.0/0',
            'ingress.3133039999.security_group_id': '',
            'ingress.3133039999.security_group_name': '',
            'ingress.3133039999.security_group_owner_id': '',
            'publicly_accessible': 'false',
            'destroy': True
        }
        self.rc = ResourceContainer(test_dict)

    def test_get_by_key(self):
        self.assertEqual(self.rc['parameter.#'], '1')
        self.assertEqual(self.rc['ingress.3133039999.cidr'], '0.0.0.0/0')
        self.assertEqual(self.rc['publicly_accessible'], 'false')
        self.assertEqual(self.rc['destroy'], True)

    def test_get_by_regex(self):
        self.assertEqual(self.rc['^ingress.3133039999.cidr$'], ['0.0.0.0/0'])
        self.assertEqual(self.rc['^ingress.[0-9]+.cidr$'], ['0.0.0.0/0'])
        self.assertEqual(len(self.rc['^ingress.*$']), 4)
        self.assertEqual(len(self.rc['^.*$']), 9)

    def test_key_not_exist(self):
        with self.assertRaises(KeyError):
            self.rc['not_exist_key']
