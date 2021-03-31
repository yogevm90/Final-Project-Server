import os
from unittest import mock

from utilities.qrcode_creator.qrcode_creator import QRCodeCreator


def test_qrcode_creator_create_regular_flow():
    save_to = os.path.join(os.path.dirname(__file__), "results", "test.png")

    QRCodeCreator().create(save_to=save_to,
                           data={"mock1": 1, "mock2": 2},
                           fill_color="yellow",
                           back_color="blue")


@mock.patch("utilities.qrcode_creator.qrcode_creator.qrcode")
def test_qrcode_creator_create_called(qrcode_mock):
    QRCodeCreator().create(data={})

    assert qrcode_mock.QRCode().add_data.called
    assert qrcode_mock.QRCode().make.called
    assert qrcode_mock.QRCode().make_image.called
    assert not qrcode_mock.QRCode().make_image().save.called


@mock.patch("utilities.qrcode_creator.qrcode_creator.qrcode")
@mock.patch("builtins.open")
def test_qrcode_creator_create_save_called(open_mock, qrcode_mock):
    QRCodeCreator().create(data={},
                           save_to="123")

    assert qrcode_mock.QRCode().make_image().save.called


def test_qrcode_creator_create_regular_flow_url():
    save_to = os.path.join(os.path.dirname(__file__), "results", "test_url.png")

    QRCodeCreator().create(save_to=save_to,
                           data={"url": "https://www.google.com", "mock2": 2})
