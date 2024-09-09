from setuptools import setup, find_packages

setup(
    name="ethos_ai",
    version="0.1.0",  # Version number
    packages=find_packages(),  # Automatically find all sub-packages
    install_requires=[],
    python_requires=">=3.9",  # Supported Python versions
    author="Robert Alexander Massinger",
    author_email="robert.alexander.massinger@outlook.de",
    description="Implementation of a EthosAI Life individual based on the Current Life Imagination Model (CLIM)",
    long_description=open("EthosAI.md").read(),  # Read the long description from a file
    long_description_content_type="text/markdown",  # The type of the long description (e.g., Markdown)
    # url="https://github.com/yourusername/my_library",  # The URL of your project, e.g., on GitHub
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",  # Classification for MPL 2.0
        "Operating System :: OS Independent",
    ],
    license="MPL-2.0",  # Specification of the license type
    license_files=[
        "LICENSE"
    ],  # Reference to the license file containing the copyright notice
)
