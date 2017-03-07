from setuptools import setup

setup(
    name='terraform_validator',
    version='0.1',
    description='Utility that enforces certain terraform config choices based on input rules.',
    keywords='terraform',
    url='https://github.com/ApplauseAQI/terraform-validator',
    author='Bojiang Jin',
    author_email='bjin@applause.com',
    packages=['terraform_validator'],
    scripts=['bin/validate-tfplan'],
    install_requires=[],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True
)
