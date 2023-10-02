import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='anubis',
    version='0.0.1',
    author='Oleh Krainyk',
    author_email='oleh@cuttingedgeai.com',
    description='Location calculator',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/CuttingEdgeAI/anubis.git',
    project_urls = {
        "Bug Tracker": "https://github.com/CuttingEdgeAI/anubis/issues"
    },
    license='Private',
    packages=['anubis'],
    install_requires=['wheel'],
)
