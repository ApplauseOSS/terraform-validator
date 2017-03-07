from unittest import TestCase
from terraform_validator.validator import TerraformValidator


class TestValidator(TestCase):
    def setUp(self):
        self.validator = TerraformValidator([
            {
                "resource": "aws_db_instance",
                "rules": [
                    {
                        "name": "encryption must be enabled",
                        "expr": "R['storage_encrypted']=='true'"
                    },
                    {
                        "name": "multi-az must be enabled",
                        "expr": "R['multi_az']=='true'"
                    },
                    {
                        "name": 'must allocated no less then 10GB',
                        "expr": "int(R['allocated_storage']) > 10"
                    }
                ]
            },
            {
                "resource": "aws_security_group_rule",
                "rules": [
                    {
                        "name": "no ingress security group rule should be open to the public",
                        "expr": "R['type'] != 'ingress' or all([val != '0.0.0.0/0' "
                                "for val in R['^cidr_blocks.[0-9]+$']])"
                    }
                ]
            },
            {
                "resource": "aws_db_security_group",
                "rules": [
                    {
                        "name": "no db ingress should be open to the public",
                        "expr": "all([val != '0.0.0.0/0' for val in R['^ingress.[0-9]+.cidr$']])"
                    }
                ]
            }
        ])

    def test_get_resource_type(self):
        self.assertEqual(self.validator._get_resource_type('aws_db_security_group.group1'), 'aws_db_security_group')
        self.assertEqual(self.validator._get_resource_type('ingress.1.cidr'), 'ingress')
        self.assertEqual(self.validator._get_resource_type('aws_db_security_group'), 'aws_db_security_group')

    def test_validate_single_rule(self):
        # test use key
        self.assertFalse(self.validator.validate_rule({"expr": "R['multi_az']=='true'"}, {}))
        self.assertTrue(self.validator.validate_rule({"expr": "R['multi_az']=='true'"}, {'multi_az': 'true'}))

        # test use regex
        self.assertFalse(self.validator.validate_rule({"expr": "any([val > 100 for val in R['^rule.[0-9]*$']])"},
                                                      {'rule.1': 100, 'rule.2': 85, 'rule.3': 23}))
        self.assertTrue(self.validator.validate_rule({"expr": "all([val > 0 for val in R['^rule.[0-9]*$']])"},
                                                     {'rule.1': 100, 'rule.2': 85, 'rule.3': 23}))

        # test invalid expression
        self.assertFalse(self.validator.validate_rule({"expr": "wubalubadubdub!"}, {}))

        # skip validation on resource being destroyed
        self.assertTrue(self.validator.validate_rule({"expr": "R['multi_az']=='true'"}, {'destroy': True}))

    def test_validate(self):
        test_tf_plan_obj = {
            "aws_db_instance.my_app_event_store": {
                "allocated_storage": "100",
                "destroy": False,
                "engine": "mysql",
                "multi_az": "",
                "name": "botesttf",
                "storage_encrypted": "true",
                "storage_type": "",
                "tags.%": "1",
                "tags.Name": "botest-tf",
                "username": "user",
                "vpc_security_group_ids.#": ""
            },
            "aws_db_security_group.default": {
                "arn": "",
                "description": "Managed by Terraform",
                "destroy": False,
                "destroy_tainted": False,
                "id": "",
                "ingress.#": "1",
                "ingress.3133039999.cidr": "0.0.0.0/0",
                "ingress.3133039999.security_group_id": "",
                "ingress.3133039999.security_group_name": "",
                "ingress.3133039999.security_group_owner_id": "",
                "name": "rds_sg"
            },
            "aws_elasticache_parameter_group.redis_default": {
                "description": "Managed by Terraform",
                "destroy": False,
                "destroy_tainted": False,
                "family": "redis3.2",
                "id": "",
                "name": "bo-elasticache-redis",
                "parameter.#": "1",
                "parameter.2943476575.name": "cluster-enabled",
                "parameter.2943476575.value": "no"
            },
            "aws_security_group_rule.allow_all": {
                "cidr_blocks.#": "1",
                "cidr_blocks.0": "0.0.0.0/0",
                "destroy": False,
                "destroy_tainted": False,
                "from_port": "0",
                "id": "",
                "protocol": "tcp",
                "security_group_id": "${aws_security_group.bo_sg.id}",
                "self": "false",
                "source_security_group_id": "",
                "to_port": "65535",
                "type": "ingress"
            },
            "destroy": False
        }

        expected_errors = [
            ('aws_security_group_rule.allow_all', 'no ingress security group rule should be open to the public'),
            ('aws_db_security_group.default', 'no db ingress should be open to the public'),
            ('aws_db_instance.my_app_event_store', 'multi-az must be enabled')
        ]

        errors = self.validator.validate(test_tf_plan_obj)
        self.assertEqual(sorted(errors), sorted(expected_errors))
