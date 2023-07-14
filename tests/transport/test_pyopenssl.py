"""
This file is copied from
https://github.com/urllib3/urllib3/blob/2.0.3/test/contrib/test_pyopenssl.py
with slight modifications. Only TestPyOpenSSLHelpers are kept.
"""

from __future__ import annotations

import os

from cryptography import x509
import mock
from OpenSSL.crypto import FILETYPE_PEM, load_certificate

from google.auth.transport.pyopenssl import (
    _dnsname_to_stdlib,
    get_subj_alt_name,
    inject_into_urllib3,
)


inject_into_urllib3()


class TestPyOpenSSLHelpers(object):
    """
    Tests for PyOpenSSL helper functions.
    """

    def test_dnsname_to_stdlib_simple(self):
        """
        We can convert a dnsname to a native string when the domain is simple.
        """
        name = "उदाहरण.परीक"
        expected_result = "xn--p1b6ci4b4b3a.xn--11b5bs8d"

        assert _dnsname_to_stdlib(name) == expected_result

    def test_dnsname_to_stdlib_leading_period(self):
        """
        If there is a . in front of the domain name we correctly encode it.
        """
        name = ".उदाहरण.परीक"
        expected_result = ".xn--p1b6ci4b4b3a.xn--11b5bs8d"

        assert _dnsname_to_stdlib(name) == expected_result

    def test_dnsname_to_stdlib_leading_splat(self):
        """
        If there's a wildcard character in the front of the string we handle it
        appropriately.
        """
        name = "*.उदाहरण.परीक"
        expected_result = "*.xn--p1b6ci4b4b3a.xn--11b5bs8d"

        assert _dnsname_to_stdlib(name) == expected_result

    @mock.patch("google.auth.transport.pyopenssl.log.warning")
    def test_get_subj_alt_name(self, mock_warning):
        """
        If a certificate has two subject alternative names, cryptography raises
        an x509.DuplicateExtension exception.
        """
        path = os.path.join(
            os.path.join(os.path.dirname(__file__), os.path.pardir),
            "data",
            "duplicate_san.pem",
        )
        with open(path) as fp:
            cert = load_certificate(FILETYPE_PEM, fp.read())

        assert get_subj_alt_name(cert) == []

        assert mock_warning.call_count == 1
        assert isinstance(mock_warning.call_args[0][1], x509.DuplicateExtension)
