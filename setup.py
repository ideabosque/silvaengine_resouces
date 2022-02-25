from setuptools import find_packages, setup

# from setuptools.command.install import install


# class InstallCommand(install):
#     def run(self):
#         with open("f:\install.log", "a") as fd:
#             fd.write("Test\n")
#         # Code
#         install.run(self)


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
        "SilvaEngine-Utility",
        "pynamodb",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    # cmdclass={
    #     "install": InstallCommand,
    # },
)
