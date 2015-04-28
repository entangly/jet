from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file

setup(
    name='jet',
            
    version='0.3.2',
            
    description='A simple to use, yet powerful version control system',
            
    long_description="See www.jetvc.co.uk",
            
    url='https://github.com/entangly/jet/',
            
    author='Connor Swain',
            
    author_email='connor@bradingsoftware.co.uk',
            
    license='MIT',
            
    classifiers=[
                'Development Status :: 3 - Alpha',
        
                'Intended Audience :: Developers',
        
                'Topic :: Software Development :: Version Control',
                
                'License :: OSI Approved :: MIT License',

                'Programming Language :: Python :: 2.7',
    ],
            
    keywords='version control jet',
            
    packages=find_packages(),

    entry_points={'console_scripts': ['jet = jet_files.jet:run'], },

            
    install_requires=['requests', ],

    include_package_data=True,

    package_data={'jet_files': ['jet_files/tests/*']},
)
