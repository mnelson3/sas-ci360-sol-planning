#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for SAS CI360 Planning Module

Comprehensive test suite for the CI360PlanningBase class and its APIs.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch
from typing import Dict, Any

from sasci360solplanning.base import CI360PlanningBase, CI360PlanningConfig, CI360PlanningError


class TestCI360PlanningConfig(unittest.TestCase):
    """Test cases for CI360PlanningConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CI360PlanningConfig()
        self.assertEqual(config.algorithm, "HS256")
        self.assertEqual(config.api_base, "/marketingPlanning")
        self.assertEqual(config.encoding, "utf-8")
        self.assertIsNone(config.host)
        self.assertIsNone(config.secret_key)
        self.assertIsNone(config.tenant_id)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_backoff, 0.5)
        self.assertTrue(config.enable_compression)
        self.assertEqual(config.max_campaigns_per_user, 100)
        self.assertEqual(config.max_audience_size, 1000000)

    def test_custom_config(self):
        """Test custom configuration values."""
        config = CI360PlanningConfig(
            host="https://api.example.com",
            secret_key="test-secret",
            tenant_id="test-tenant",
            timeout=60,
            max_campaigns_per_user=50
        )
        self.assertEqual(config.host, "https://api.example.com")
        self.assertEqual(config.secret_key, "test-secret")
        self.assertEqual(config.tenant_id, "test-tenant")
        self.assertEqual(config.timeout, 60)
        self.assertEqual(config.max_campaigns_per_user, 50)


class TestCI360PlanningBase(unittest.TestCase):
    """Test cases for CI360PlanningBase class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CI360PlanningConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id"
        )

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    def test_initialization_success(self, mock_encryption_class, mock_session_class):
        """Test successful initialization."""
        mock_encryption = Mock()
        mock_encryption.generate_jwt.return_value = "test-token"
        mock_encryption_class.return_value = mock_encryption

        mock_session = Mock()
        mock_session_class.return_value = mock_session

        client = CI360PlanningBase(self.config)

        self.assertEqual(client.config, self.config)
        self.assertEqual(client.token, "test-token")

    # Campaign Management Tests

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_get_campaigns_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async campaign retrieval."""
        mock_request.return_value = {"campaigns": [], "total": 0}

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.get_campaigns_async(limit=25, offset=50))

        self.assertEqual(result, {"campaigns": [], "total": 0})
        mock_request.assert_called_once_with(
            "GET", "/campaigns",
            params={"limit": 25, "offset": 50}
        )

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_get_campaign_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async single campaign retrieval."""
        campaign_data = {
            "id": "camp-123",
            "name": "Holiday Campaign 2025",
            "status": "draft",
            "audienceId": "aud-456"
        }
        mock_request.return_value = campaign_data

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.get_campaign_async("camp-123"))

        self.assertEqual(result["name"], "Holiday Campaign 2025")
        mock_request.assert_called_once_with("GET", "/campaigns/camp-123")

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_create_campaign_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async campaign creation."""
        campaign_data = {
            "name": "New Year Campaign",
            "description": "Welcome 2026 campaign",
            "audienceId": "aud-123",
            "channels": ["email", "sms"]
        }
        mock_request.return_value = {"id": "camp-456", **campaign_data}

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.create_campaign_async(campaign_data))

        self.assertEqual(result["id"], "camp-456")
        mock_request.assert_called_once_with("POST", "/campaigns", data=campaign_data)

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_update_campaign_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async campaign update."""
        update_data = {"name": "Updated Campaign Name", "status": "active"}
        mock_request.return_value = {"id": "camp-123", **update_data}

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.update_campaign_async("camp-123", update_data))

        self.assertEqual(result["name"], "Updated Campaign Name")
        mock_request.assert_called_once_with("PUT", "/campaigns/camp-123", data=update_data)

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_delete_campaign_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async campaign deletion."""
        mock_request.return_value = None

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.delete_campaign_async("camp-123"))

        self.assertTrue(result)
        mock_request.assert_called_once_with("DELETE", "/campaigns/camp-123")

    # Audience Management Tests

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_get_audiences_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async audience retrieval."""
        mock_request.return_value = {"audiences": [], "total": 0}

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.get_audiences_async(limit=30, offset=60))

        self.assertEqual(result, {"audiences": [], "total": 0})
        mock_request.assert_called_once_with(
            "GET", "/audiences",
            params={"limit": 30, "offset": 60}
        )

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_create_audience_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async audience creation."""
        audience_data = {
            "name": "High-Value Customers",
            "description": "Customers with >$500 lifetime value",
            "criteria": {"lifetimeValue": {"gt": 500}}
        }
        mock_request.return_value = {"id": "aud-789", **audience_data}

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.create_audience_async(audience_data))

        self.assertEqual(result["name"], "High-Value Customers")
        mock_request.assert_called_once_with("POST", "/audiences", data=audience_data)

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_estimate_audience_size_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async audience size estimation."""
        criteria = {"age": {"gte": 25, "lte": 65}, "country": "US"}
        mock_request.return_value = {"estimatedSize": 125000, "confidence": 0.95}

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.estimate_audience_size_async(criteria))

        self.assertEqual(result["estimatedSize"], 125000)
        mock_request.assert_called_once_with("POST", "/audiences/estimate", data=criteria)

    # Campaign Optimization Tests

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_optimize_campaign_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async campaign optimization."""
        optimization_params = {"goal": "maximize_conversions", "budget": 5000}
        mock_request.return_value = {
            "recommendations": [
                {"type": "channel_mix", "suggestedChannels": ["email", "sms", "push"]},
                {"type": "timing", "suggestedSchedule": "weekdays_9am_5pm"}
            ]
        }

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.optimize_campaign_async("camp-123", optimization_params))

        self.assertEqual(len(result["recommendations"]), 2)
        expected_payload = {"campaignId": "camp-123", "optimizationParams": optimization_params}
        mock_request.assert_called_once_with("POST", "/campaigns/optimize", data=expected_payload)

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_get_campaign_analytics_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async campaign analytics retrieval."""
        mock_request.return_value = {
            "campaignId": "camp-123",
            "impressions": 50000,
            "clicks": 2500,
            "conversions": 125,
            "revenue": 25000.00
        }

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.get_campaign_analytics_async(
            "camp-123",
            start_date="2025-12-01",
            end_date="2025-12-13"
        ))

        self.assertEqual(result["clicks"], 2500)
        expected_params = {
            "campaignId": "camp-123",
            "startDate": "2025-12-01",
            "endDate": "2025-12-13"
        }
        mock_request.assert_called_once_with("GET", "/analytics/campaigns", params=expected_params)

    # Template Management Tests

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_get_campaign_templates_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async campaign template retrieval."""
        mock_request.return_value = {"templates": [], "total": 0}

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.get_campaign_templates_async(category="promotional", limit=15))

        self.assertEqual(result, {"templates": [], "total": 0})
        expected_params = {"category": "promotional", "limit": 15, "offset": 0}
        mock_request.assert_called_once_with("GET", "/templates/campaigns", params=expected_params)

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_create_campaign_from_template_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async campaign creation from template."""
        campaign_data = {"name": "My Campaign", "audienceId": "aud-123"}
        mock_request.return_value = {
            "id": "camp-999",
            "name": "My Campaign",
            "templateId": "tmpl-456",
            "status": "draft"
        }

        client = CI360PlanningBase(self.config)
        result = asyncio.run(client.create_campaign_from_template_async("tmpl-456", campaign_data))

        self.assertEqual(result["id"], "camp-999")
        expected_payload = {"templateId": "tmpl-456", "campaignData": campaign_data}
        mock_request.assert_called_once_with("POST", "/campaigns/from-template", data=expected_payload)

    # Synchronous method tests

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_get_campaigns_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous campaign retrieval."""
        mock_request.return_value = {"campaigns": [], "total": 0}

        client = CI360PlanningBase(self.config)
        result = client.get_campaigns(limit=25)

        self.assertEqual(result["total"], 0)

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_create_campaign_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous campaign creation."""
        campaign_data = {"name": "Test Campaign"}
        mock_request.return_value = {"id": "camp-123", **campaign_data}

        client = CI360PlanningBase(self.config)
        result = client.create_campaign(campaign_data)

        self.assertEqual(result["id"], "camp-123")

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_estimate_audience_size_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous audience size estimation."""
        criteria = {"age": {"gte": 18}}
        mock_request.return_value = {"estimatedSize": 50000}

        client = CI360PlanningBase(self.config)
        result = client.estimate_audience_size(criteria)

        self.assertEqual(result["estimatedSize"], 50000)


class TestCI360PlanningErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CI360PlanningConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id"
        )

    @patch('sasci360solplanning.base.requests.Session')
    @patch('sasci360solplanning.base.Encryption')
    @patch('sasci360solplanning.base.CI360PlanningBase._make_request_async')
    def test_validation_error_handling(self, mock_request, mock_encryption_class, mock_session_class):
        """Test validation error handling."""
        from sasci360solplanning.base import CI360PlanningValidationError
        mock_request.side_effect = CI360PlanningValidationError("Invalid campaign data")

        client = CI360PlanningBase(self.config)

        with self.assertRaises(CI360PlanningValidationError):
            asyncio.run(client.create_campaign_async({"invalid": "data"}))


if __name__ == '__main__':
    unittest.main()