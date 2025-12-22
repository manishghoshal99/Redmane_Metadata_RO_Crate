from setuptools import setup, find_packages

setup(
    name="redmane-metadata-generator",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["numpy", "pandas", "rocrate"],
    entry_points={
        "console_scripts": ["redmane-ingest=redmane.generator:main"]
    },
    include_package_data=True,
    package_data={
        "redmane": ["sample_metadata/*.json"]
    },
    author="REDMANE Team",
    description="Metadata generator and RO-Crate packager for REDMANE datasets",
    python_requires=">=3.7",
)
