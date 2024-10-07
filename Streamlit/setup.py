from setuptools import find_packages, setup
from typing import List

HYPHEN_E = "-e ."

def get_requirements(filepath:str)->List[str]:
    '''
    This function return the list of requirements 
    '''
    requirements = []
    with open (filepath, 'r') as file:
        requirements = file.readlines()
        requirements = [x.strip() for x in requirements]

        if HYPHEN_E in requirements:
            requirements.remove(HYPHEN_E)
    return requirements

setup(
    name='Stock_price_prediction',
    version='0.1',
    author= 'Mohamed Tharif B',
    author_email= 'mohammedtharif30@gmail.com',
    packages= find_packages(),
    requires= get_requirements('requirements.txt')
)
