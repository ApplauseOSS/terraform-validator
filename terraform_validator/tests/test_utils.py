from unittest import TestCase
from terraform_validator import utils


class TestUtils(TestCase):

    def test_read_rules_file(self):
        rules_obj = utils.read_rules_file('terraform_validator/tests/resources/test_rules.json')
        self.assertEqual(len(rules_obj), 3)
        self.assertEqual(rules_obj[0][u'resource'], u'aws_db_instance')
        self.assertEqual(rules_obj[1][u'resource'], u'aws_security_group_rule')
        self.assertEqual(rules_obj[2][u'resource'], u'aws_db_security_group')

    def test_read_plan_file(self):
        plan_obj = utils.read_plan_file('terraform_validator/tests/resources/test1.tfplan')
        self.assertEqual(len(plan_obj), 7)
        self.assertIn("aws_db_instance.my_app_event_store", plan_obj)
        self.assertIn("aws_db_instance.my_app_event_store", plan_obj)
        self.assertIn("aws_db_instance.my_app_event_store_2", plan_obj)
        self.assertIn("allocated_storage", plan_obj["aws_db_instance.my_app_event_store_2"])

    def test_read_bad_plan_file(self):
        try:
            utils.read_plan_file('terraform_validator/tests/resources/test_rules.json')
            self.assertFalse('Parsing bad plan did not fail (it should have).')
        except utils.TFJsonException, e:
            self.assertTrue('Parsing bad plan failed (this is a good thing).')