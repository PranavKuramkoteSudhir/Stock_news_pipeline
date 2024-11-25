from setuptools import find_packages, setup
from typing import List

def get_requirements(file_path: str) -> List[str]:
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        # Removed newline characters from each requirement.
        requirements = [req.replace('\n', '') for req in requirements]

    # Removed the editable installation requirement '-e .' if present.
    if '-e .' in requirements:
        requirements.remove('-e .')
    return requirements

setup(
name='Stock news pipeline',
version='0.0.1',
author='Pranav Kuramkote Sudhir',
author_email='pranav.pani@gmail.com',  
packages=find_packages(),
install_requires=get_requirements('requirements.txt')  
)