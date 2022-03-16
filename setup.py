import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

# get version
env = {}
with open("figurator/version.py") as f:
	exec(f.read(), env)
version = env["__version__"]

# get requirements
with open("requirements.txt") as f:
	install_requires = f.readlines()

setuptools.setup(
	name = "figurator",
	version = version,
	author = "Christopher Pyles",
	description = "User configuration manager and documenter",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	url = "https://github.com/chrispyles/confit",
	license = "MIT",
	packages = setuptools.find_packages(exclude=["test"]),
	classifiers = [
		"Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
	],
	install_requires=install_requires,
)
