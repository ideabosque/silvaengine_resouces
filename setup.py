from setuptools import find_packages, setup

setup(
    name="SilvaEngine-Resource",
    version="0.0.1",
    author="Idea Bosque",
    author_email="ideabosque@gmail.com",
    description="SilvaEngine Resource",
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms="Linux",
    install_requires=[
        "silvaengine_utility",
        "pynamodb>=5.0.0",
        "graphene>=3.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "black>=25.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "graphdoc>=0.3.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
