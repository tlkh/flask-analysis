# flask-static-analysis

Part of project for ISTD MSSD 51.503: Secure Software Engineering

## Static Analysis Performed on Flask

Done:

* flake8 + security plugins
* dependencies scanning
* audit for hardcoded secrets

TODO:

* https://github.com/facebook/pyre-check

## Black Box Testing

### Generate SSL cert

```shell
pip install pyopenssl

openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### Running

```shell
python3 -m unittest BlackBoxTests
```