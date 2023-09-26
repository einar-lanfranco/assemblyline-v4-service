from test import setup_module

from assemblyline_v4_service.common.ocr import *


def test_ocr_detections():
    assert ocr_detections("./test/b32969aa664e3905c20f865cdd7b921f922678f5c3850c78e4c803fbc1757a8e") == {
        'ransomware': [
            "YOUR FILES HAVE BEEN ENCRYPTED AND YOU WON'T BE ABLE TO "
            'DECRYPT THEM.',
            'YOU CAN BUY DECRYPTION SOFTWARE FROM US, THIS SOFTWARE WILL '
            'ALLOW YOU TO RECOVER ALL OF YOUR DATA AND',
            'RANSOMWARE FROM YOUR COMPUTER. THE PRICE OF THE SOFTWARE IS '
            '$.2..%.. PAYMENT CAN BE MADE IN BITCOIN OR XMR.',
            'How 00! PAY, WHERE DO | GET BITCOIN OR XMR?',
            'YOURSELF TO FIND OUT HOW TO BUY BITCOIN OR XMR.',
            'PAYMENT INFORMATION: SEND $15, TO ONE OF OUR CRYPTO '
            'ADDRESSES, THEN SEND US EMAIL WITH PAYMENT',
            "CONFIRMATION AND YOU'LL GET THE DECRYPTION SOFTWARE IN "
            'EMAIL.'
        ],
    }


def test_detections():
    setup_module()
    # No detection
    assert detections("blah") == {}

    # Containing a banned string
    assert detections("blah\nrecover them\ndonotscanme") == {"banned": ["donotscanme"]}

    # Containing a single ransomware string
    assert detections("blah\nrecover them\nblah") == {}

    # Containing two ransomware strings
    assert detections("blah\nrecover them\nblah\nencrypt") == {"ransomware": ["recover them", "encrypt"]}
