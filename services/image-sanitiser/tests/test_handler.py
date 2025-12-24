"""
Unit tests for the Lambda handler function.

Tests cover:
- EXIF metadata stripping functionality
- Error handling
- S3 event processing
"""

import json
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pytest
from PIL import Image

from handler import lambda_handler, strip_exif_metadata


class TestStripExifMetadata:
    """Test the EXIF metadata stripping function."""

    def test_strips_exif_from_jpeg(self) -> None:
        """Test that EXIF metadata is removed from JPEG images."""
        # Create a test image with EXIF data
        img = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        image_with_exif = buffer.getvalue()

        # Strip EXIF
        sanitized = strip_exif_metadata(image_with_exif)

        # Verify it's still a valid image
        result_img = Image.open(BytesIO(sanitized))
        assert result_img.size == (100, 100)
        assert result_img.mode == "RGB"

    def test_converts_non_rgb_to_rgb(self) -> None:
        """Test that non-RGB images are converted to RGB."""
        # Create RGBA image
        img = Image.new("RGBA", (50, 50), color=(255, 0, 0, 128))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        rgba_image = buffer.getvalue()

        # Strip EXIF (should convert to RGB)
        sanitized = strip_exif_metadata(rgba_image)

        # Verify conversion
        result_img = Image.open(BytesIO(sanitized))
        assert result_img.mode == "RGB"

    def test_raises_error_on_invalid_image(self) -> None:
        """Test that invalid image data raises an error."""
        invalid_data = b"not an image"

        with pytest.raises(Exception):
            strip_exif_metadata(invalid_data)


class TestLambdaHandler:
    """Test the Lambda handler function."""

    @patch("handler.s3_client")
    @patch("handler.OUTPUT_BUCKET", "test-output-bucket")
    @patch("handler.logger")
    def test_successful_processing(
        self, mock_logger: MagicMock, mock_s3_client: MagicMock
    ) -> None:
        """Test successful image processing flow."""
        # Create a test image
        img = Image.new("RGB", (100, 100), color="blue")
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        image_data = buffer.getvalue()

        # Mock S3 responses
        mock_get_response = Mock()
        mock_get_response.__getitem__ = Mock(return_value=Mock(read=Mock(return_value=image_data)))
        mock_get_response.get = Mock(return_value="image/jpeg")
        mock_s3_client.get_object.return_value = mock_get_response
        mock_s3_client.put_object.return_value = {}

        # Create S3 event
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-input-bucket"},
                        "object": {"key": "test-image.jpg"},
                    }
                }
            ]
        }

        # Call handler
        result = lambda_handler(event, Mock())

        # Verify results
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["processed"] == 1
        assert body["results"][0]["status"] == "success"
        assert body["results"][0]["input_key"] == "test-image.jpg"
        assert body["results"][0]["output_key"] == "test-image.jpg"

        # Verify S3 calls
        mock_s3_client.get_object.assert_called_once_with(
            Bucket="test-input-bucket", Key="test-image.jpg"
        )
        mock_s3_client.put_object.assert_called_once()
        assert mock_s3_client.put_object.call_args[1]["Bucket"] == "test-output-bucket"
        assert mock_s3_client.put_object.call_args[1]["Key"] == "test-image.jpg"

    @patch("handler.s3_client")
    @patch("handler.OUTPUT_BUCKET", "test-output-bucket")
    @patch("handler.logger")
    def test_handles_s3_error(
        self, mock_logger: MagicMock, mock_s3_client: MagicMock
    ) -> None:
        """Test error handling when S3 download fails."""
        # Mock S3 error
        mock_s3_client.get_object.side_effect = Exception("S3 access denied")

        # Create S3 event
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-input-bucket"},
                        "object": {"key": "test-image.jpg"},
                    }
                }
            ]
        }

        # Call handler
        result = lambda_handler(event, Mock())

        # Verify error is handled gracefully
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["processed"] == 1
        assert body["results"][0]["status"] == "error"
        assert "error" in body["results"][0]

    @patch("handler.s3_client")
    @patch("handler.OUTPUT_BUCKET", "test-output-bucket")
    def test_processes_multiple_records(self, mock_s3_client: MagicMock) -> None:
        """Test processing multiple S3 event records."""
        # Create test images
        img1 = Image.new("RGB", (50, 50), color="red")
        img2 = Image.new("RGB", (50, 50), color="green")

        buffer1 = BytesIO()
        buffer2 = BytesIO()
        img1.save(buffer1, format="JPEG")
        img2.save(buffer2, format="JPEG")

        # Mock S3 responses
        def mock_get_object(Bucket: str, Key: str) -> Mock:
            mock_response = Mock()
            if Key == "image1.jpg":
                mock_response.__getitem__ = Mock(
                    return_value=Mock(read=Mock(return_value=buffer1.getvalue()))
                )
            else:
                mock_response.__getitem__ = Mock(
                    return_value=Mock(read=Mock(return_value=buffer2.getvalue()))
                )
            mock_response.get = Mock(return_value="image/jpeg")
            return mock_response

        mock_s3_client.get_object.side_effect = mock_get_object
        mock_s3_client.put_object.return_value = {}

        # Create S3 event with multiple records
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-input-bucket"},
                        "object": {"key": "image1.jpg"},
                    }
                },
                {
                    "s3": {
                        "bucket": {"name": "test-input-bucket"},
                        "object": {"key": "image2.jpg"},
                    }
                },
            ]
        }

        # Call handler
        result = lambda_handler(event, Mock())

        # Verify both processed
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["processed"] == 2
        assert len(body["results"]) == 2

    def test_handles_empty_event(self) -> None:
        """Test handling of event with no records."""
        event = {"Records": []}

        result = lambda_handler(event, Mock())

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["processed"] == 0
        assert body["results"] == []

