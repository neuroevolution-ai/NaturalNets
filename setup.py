from setuptools import setup, find_packages


setup(
    name="naturalnets",
    version="0.1.0",
    description="NaturalNets implmented in Python",
    url="https://github.com/neuroevolution-ai/NaturalNets",
    author="Daniel Zimmermann",
    author_email="dzimmer@fzi.de",
    license="MIT",
    packages=find_packages(),
    install_requires=["wheel", "attrs", "deap", "numpy", "gym", "scipy", "torch",
                      "procgen", "opencv-python", "cma", "matplotlib", "pandas", "py-cpuinfo"]
)
