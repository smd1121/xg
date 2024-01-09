import setuptools

setuptools.setup(
    name="xg",
    packages=setuptools.find_packages(),
    install_requires=["typer", "rich"],
    entry_points={"console_scripts": ["xg = xg.cli:app"]},
)
