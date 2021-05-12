import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="s3-trigger",
    version="0.0.1",

    description="A CDK Python app for deploying an S3 bucket with a trigger to write to a Dynamo table",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "s3_trigger"},
    packages=setuptools.find_packages(where="s3_trigger"),

    python_requires=">=3.8",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
