import pytest

from changelog_helper.loaders.html import remove_base64_image


def test_remove_base64_image_with_image():
    markdown_text = "Here is an image ![alt text](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA)"
    expected_result = "Here is an image "
    assert remove_base64_image(markdown_text) == expected_result


def test_remove_base64_image_without_image():
    markdown_text = "Here is some text without an image."
    expected_result = "Here is some text without an image."
    assert remove_base64_image(markdown_text) == expected_result


def test_remove_base64_image_with_multiple_images():
    markdown_text = "Image1 ![alt text](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA) and Image2 ![alt text](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUB)"
    expected_result = "Image1  and Image2 "
    assert remove_base64_image(markdown_text) == expected_result


def test_remove_base64_image_with_different_formats():
    markdown_text = "Image1 ![alt text](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD) and Image2 ![alt text](data:image/gif;base64,R0lGODlhPQBEAPeoAJosM//AwO/AwHV)"
    expected_result = "Image1  and Image2 "
    assert remove_base64_image(markdown_text) == expected_result


def test_remove_base64_image_with_no_base64():
    markdown_text = "Here is an image ![alt text](http://example.com/image.png)"
    expected_result = "Here is an image ![alt text](http://example.com/image.png)"
    assert remove_base64_image(markdown_text) == expected_result
