"""
Setup configuration for Markdown Documentation Viewer
"""

from setuptools import setup, find_packages
import os

# Read version from package
def read_version():
    version_file = os.path.join('docnexus', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '1.0.0'

# Read long description from README
def read_long_description():
    readme_file = os.path.join('docs', 'USER_GUIDE.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read requirements
def read_requirements():
    requirements_file = 'requirements.txt'
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='docnexus',
    version=read_version(),
    author='DocNexus Maintainers',
    author_email='maintainers@docnexus.org',
    maintainer='DocNexus Open Source Community',
    description='DocNexus - The Ultimate All-in-One Document Engine',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/omnidoc-org/docnexus',
    packages=find_packages(exclude=['tests', 'tests.*', 'releases', 'build', 'dist']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: Markup',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
        'console_scripts': [
            'docnexus=docnexus.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'docnexus': [
            'templates/*.html',
        ],
    },
    keywords='markdown documentation viewer executive presentation toc mermaid diagrams',
    project_urls={
        'Documentation': 'https://github.com/omnidoc-org/docnexus/tree/main/docs',
        'Source': 'https://github.com/omnidoc-org/docnexus',
        'Changelog': 'https://github.com/omnidoc-org/docnexus/blob/main/docs/CHANGELOG.md',
        'Bug Tracker': 'https://github.com/omnidoc-org/docnexus/issues',
    },
)
