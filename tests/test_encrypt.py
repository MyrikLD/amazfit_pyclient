from unittest.mock import Mock, patch

from amazfit_pyclient.chunked_encoder import ChunkedEncoder


def test_encrypt():
    a = ChunkedEncoder(Mock())
    a.write_handle = 46
    a.set_encryption_parameters(
        encrypted_sequence_number=0xF5C7CB0A - 1,
        final_shared_session_aes=b"\x14\xcd\x905\xd6\xb9U;\xe8$\x8f\x85\x0f!j\xa5",
    )
    with patch("chunked_encoder.chunked_encoder.encrypt_aes") as mock:
        a.encrypt(
            b'\x02B\x01\x94>\x00\x00\x00{"errorCode":-2001,"httpStatusCode":404,"message":"Not found"}',
        )

    mock.assert_called_once_with(
        b'\x02B\x01\x94>\x00\x00\x00{"errorCode":-2001,"httpStatusCode":404,"message":"Not found"}\t\xcb\xc7\xf5\t<\x9f]\x00\x00',
        b":\xe3\xbe\x1b\xf8\x97{\x15\xc6\n\xa1\xab!\x0fD\x8b",
    )


def test_encrypt_1():
    a = ChunkedEncoder(Mock())
    a.write_handle = 6
    a.set_encryption_parameters(
        encrypted_sequence_number=0xFF55B4B2 - 1,
        final_shared_session_aes=b"\xbe\xac\xed\x85\xa5\x1d&\x01\xf8\x8a9\xbb\x0e!j\xa5",
    )
    r = a.encrypt(
        b"\x01O\x07\x00\x00\xb2\x07\x07\x01\x00\xaf\x00\xb06\xc8\xcbu\x04\x00\x00\x00\x00unknown\x00\tMyrik\x00",
    )

    assert (
        r
        == b"nwq\xc8MV\xee]\xcf\x06\xaacz\x9e!\xdd\xeaGJ\xe9KWJ:\x08\xfc\x05]\xf3\x1b\x1f\xbc)-\xf82\x1e\x8c\x8a\xb09\xc4'\xee\xaeNH\x9d"
    )
