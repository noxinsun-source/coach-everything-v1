#!/usr/bin/env python
"""
Setup configuration for Coach Everything
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='coach-everything',
    version='1.0.0',
    author='Noxinsun & Claude Haiku (Anthropic)',
    author_email='KingsleyJed623@zohomail.com',
    description='Universal Task Breakdown & AI Coaching Agent for ADHD and executive function support',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/coach-everything',
    project_urls={
        'Bug Tracker': 'https://github.com/yourusername/coach-everything/issues',
        'Documentation': 'https://github.com/yourusername/coach-everything/docs',
        'Source Code': 'https://github.com/yourusername/coach-everything',
    },
    packages=find_packages(exclude=['tests', 'examples', 'docs']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Education',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'requests>=2.28.0',
        'pydantic>=2.0.0',
        'PyYAML>=6.0',
        'click>=8.0.0',
        'rich>=13.0.0',
        'feedparser>=6.0.0',
        'beautifulsoup4>=4.11.0',
        'feedparser>=6.0.0',
        'arxiv>=1.4.0',
        'anthropic>=0.7.0',
    ],
    entry_points={
        'console_scripts': [
            'coach=coach.main:cli',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
