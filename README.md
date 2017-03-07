# Terraform validator
Command line utility that validate a terraform plan file against certain rules based on input rules.

## Use cases
Before apply any terraform plan:

1. make sure no aws security group is open to the public.
2. make sure storage encryption and multi-az enabled on all aws rds instances. 
3. ... 

## Install
```
pip install terraform-validator
```

## Usage
```
validate-tfplan -p <path to .tfplan file> -r <path to your terraform rules .json file>
```
Command line exits with code 0 if all resources are valid. Exits with code 1 if validation failed
and logs validation failure to stderr.

## Define your custom terraform rules
### JSON file structure
Rules file are in .json format. The out-most object is a array.
Each element in the array defines rules for a single terraform resource type. 
```javascript
# definition of a single resource type and rules around it.
{
  "resource": "aws_db_instance",
  "rules": [
    {
      "name": "encryption should be enabled",
      "expr": "R['storage_encrypted']=='true'"
    }
  ]
}
```
Within that, ```rules``` attribute is an array of rule objects.
Each rule objects have two attributes, ```name``` and ```expr```. 
```name``` is used for identifying the purpose of this rule. 
```expr``` is used for validating the rule.

### Rule expression syntax
The rule expression is string of a python-like syntax expression that should be evaluated in the context of a resource of
 current resource type and return ```True``` (means valid) or ```False``` (means invalid).
 
A special variable ```R``` that contains all attributes of the resource is provided to the expression when its being evaluated.
Attributes can be accessed by key from ```R```, for example ```R['storage_encrypted']```.

The key string can be an attribute name or a regular expression that matches one or more attribute name. 
When the key is an attribute name, ```R[key]``` returns the value of that attribute. 
When the key is a regular expression, ```R[key]``` returns a list of values of all attributes that
match the regular expression.

For example, by using command ```terraform show my.tfplan```, you can check what attribute a resource have.
```
+ my_resource_type.my_resource
    engine:                    "mysql"
    allocated_storage:          "10"
    apply_immediately:          "<computed>"
    storage_encrypted:          "true"
    parameter.#:                "1"
    ingress.3133039999.cidr:    "0.0.0.0/0"
    ingress.3133039999.cidr:    "127.0.0.1/0"
```
Then, you can imagine that ```R['engine']``` is ```'mysql'```, ```R['^ingress.[0-9]+.cidr$']]``` is ```['0.0.0.0/0', '127.0.0.1/0']```
and write validation logic accordingly.

### Full example of a rules json:
```javascript
[
  {
    "resource": "aws_db_instance",
    "rules": [
      {
        "name": "encryption should be enabled",
        "expr": "R['storage_encrypted']=='true'"
      },
      {
        "name": "multi-az should be enabled",
        "expr": "R['multi_az']=='true'"
      }
    ]
  },
  {
    "resource": "aws_security_group_rule",
    "rules":[
      {
        "name": "no ingress security group role should be open to the public",
        "expr": "R['type'] != 'ingress' or all([val != '0.0.0.0/0' for val in R['^cidr_blocks.[0-9]+$']])"
      }
    ]
  },
  {
    "resource": "aws_db_security_group",
    "rules":[
      {
        "name": "no ingress security group role should be open to the public",
        "expr": "all([val != '0.0.0.0/0' for val in R['^ingress.[0-9]+.cidr$']])"
      }
    ]
  }
]
```

## To-dos
1. Add the ability to validate against specific resource name.
2. Add nested module validation.
3. Add Windows tfjson binary for Windows machines.
4. Add access to dynamic name value pair attribute. For example:
```
parameter.2943476575.name:  "cluster-enabled"
parameter.2943476575.value: "no"
```

Special thanks to [tfjson](https://github.com/palantir/tfjson) for providing .tfplan file parsing ability.