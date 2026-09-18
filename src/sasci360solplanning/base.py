#!/usr/bin/env python3
#
# Copyright (c) 2025 Nelson Grey LLC
# Author: Nelson Grey LLC
#
# Licensed under the Nelson Grey LLC Community License 1.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# https://github.com/mnelson3/sas-ci360-sol-planning/blob/main/LICENSE
#
# -*- coding: utf-8 -*-
"""
SAS CI360 Planning Module Base Class

Provides foundational functionality for SAS Customer Intelligence 360
planning operations, including connection management, authentication,
and campaign planning capabilities.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import jwt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class CI360PlanningConfig:
    """Configuration for CI360 Planning operations."""

    algorithm: str = "HS256"
    api_base: str = "/marketingPlanning"
    encoding: str = "utf-8"
    host: Optional[str] = None
    secret_key: Optional[str] = None
    tenant_id: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 0.5
    enable_compression: bool = True
    max_campaigns_per_user: int = 100
    max_audience_size: int = 1000000


class CI360PlanningError(Exception):
    """Base exception for CI360 Planning operations."""
    pass


class CI360PlanningAuthError(CI360PlanningError):
    """Authentication-related errors."""
    pass


class CI360PlanningConnectionError(CI360PlanningError):
    """Connection and network-related errors."""
    pass


class CI360PlanningValidationError(CI360PlanningError):
    """Data validation errors."""
    pass


class Encryption:
    """Generates signed JWTs for CI360 Planning API authentication."""

    def __init__(self, algorithm: str = "HS256", encoding: str = "utf-8") -> None:
        self.algorithm = algorithm
        self.encoding = encoding

    def generate_jwt(self, tenant_id: str, secret_key: str) -> str:
        """Generate a signed JWT scoped to the given tenant."""
        now = datetime.now(timezone.utc)
        payload = {
            "tenant_id": tenant_id,
            "iat": now,
            "exp": now + timedelta(hours=1),
        }
        return jwt.encode(payload, secret_key, algorithm=self.algorithm)


class CI360PlanningBase:
    """
    Base class for SAS CI360 Planning operations.

    Provides authentication, connection management, and common functionality
    for marketing planning and campaign management API interactions with async support.
    """

    def __init__(self, config: Optional[CI360PlanningConfig] = None) -> None:
        """
        Initialize the CI360 Planning base client.

        Args:
            config: Configuration object for CI360 Planning operations

        Raises:
            CI360PlanningValidationError: If required configuration is missing
        """
        self.config = config or CI360PlanningConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Validate configuration
        self._validate_config()

        # Initialize HTTP session with retry strategy
        self.session = self._create_session()

        # Generate authentication token
        self.token = self._generate_token()

        # Connection state
        self._connected = False

        self.logger.info("CI360 Planning Base initialized successfully")

    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        required_fields = ['host', 'secret_key', 'tenant_id']
        missing = [field for field in required_fields if not getattr(self.config, field)]

        if missing:
            raise CI360PlanningValidationError(f"Missing required configuration: {', '.join(missing)}")

        # Validate algorithm
        supported_algorithms = ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512']
        if self.config.algorithm not in supported_algorithms:
            raise CI360PlanningValidationError(f"Unsupported algorithm: {self.config.algorithm}")

        # Validate campaign limits
        if self.config.max_campaigns_per_user <= 0:
            raise CI360PlanningValidationError("max_campaigns_per_user must be positive")

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _generate_token(self) -> str:
        """Generate JWT authentication token."""
        try:
            encryption = Encryption(
                algorithm=self.config.algorithm,
                encoding=self.config.encoding
            )

            return encryption.generate_jwt(
                tenant_id=str(self.config.tenant_id),
                secret_key=str(self.config.secret_key)
            )
        except Exception as e:
            raise CI360PlanningAuthError(f"Failed to generate authentication token: {e}")

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.

        Returns:
            Dict[str, str]: Headers dictionary with authorization token
        """
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Tenant-ID": str(self.config.tenant_id)
        }

    async def validate_connection_async(self) -> bool:
        """
        Asynchronously validate connection to CI360 service.

        Returns:
            bool: True if connection is valid
        """
        try:
            # Basic health check endpoint
            health_url = urljoin(str(self.config.host), "/health")
            headers = self.get_auth_headers()

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(
                    health_url,
                    headers=headers,
                    timeout=self.config.timeout
                )
            )

            self._connected = response.status_code == 200
            return self._connected

        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            self._connected = False
            return False

    def validate_connection(self) -> bool:
        """
        Validate connection to CI360 service.

        Returns:
            bool: True if connection is valid
        """
        try:
            # Run async validation in sync context
            return asyncio.run(self.validate_connection_async())
        except Exception as e:
            self.logger.error(f"Sync connection validation failed: {e}")
            return False

    async def _make_request_async(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make asynchronous HTTP request to CI360 API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Dict[str, Any]: Response data

        Raises:
            CI360PlanningConnectionError: For network/connection errors
            CI360PlanningAuthError: For authentication errors
        """
        if not self._connected:
            await self.validate_connection_async()
            if not self._connected:
                raise CI360PlanningConnectionError("No active connection to CI360 service")

        url = urljoin(str(self.config.host) + self.config.api_base, endpoint.lstrip('/'))
        headers = self.get_auth_headers()

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=self.config.timeout
                )
            )

            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise CI360PlanningAuthError(f"Authentication failed: {e}")
            elif response.status_code >= 500:
                raise CI360PlanningConnectionError(f"Server error: {e}")
            else:
                raise CI360PlanningError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise CI360PlanningConnectionError(f"Network error: {e}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make synchronous HTTP request to CI360 API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Dict[str, Any]: Response data
        """
        try:
            return asyncio.run(self._make_request_async(method, endpoint, data, params))
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            raise

    # Campaign Management APIs

    async def get_campaigns_async(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve campaigns asynchronously.

        Args:
            limit: Maximum number of campaigns to return
            offset: Number of campaigns to skip
            filters: Optional filters for campaigns

        Returns:
            Dict containing campaign data and metadata
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return await self._make_request_async("GET", "/campaigns", params=params)

    def get_campaigns(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve campaigns synchronously."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return self._make_request("GET", "/campaigns", params=params)

    async def get_campaign_async(self, campaign_id: str) -> Dict[str, Any]:
        """
        Retrieve specific campaign data asynchronously.

        Args:
            campaign_id: Unique campaign identifier

        Returns:
            Dict containing campaign data
        """
        return await self._make_request_async("GET", f"/campaigns/{campaign_id}")

    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Retrieve specific campaign data synchronously."""
        return self._make_request("GET", f"/campaigns/{campaign_id}")

    async def create_campaign_async(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new campaign asynchronously.

        Args:
            campaign_data: Campaign configuration data

        Returns:
            Dict containing created campaign data
        """
        return await self._make_request_async("POST", "/campaigns", data=campaign_data)

    def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new campaign synchronously."""
        return self._make_request("POST", "/campaigns", data=campaign_data)

    async def update_campaign_async(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update campaign data asynchronously.

        Args:
            campaign_id: Unique campaign identifier
            campaign_data: Updated campaign data

        Returns:
            Dict containing updated campaign data
        """
        return await self._make_request_async("PUT", f"/campaigns/{campaign_id}", data=campaign_data)

    def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update campaign data synchronously."""
        return self._make_request("PUT", f"/campaigns/{campaign_id}", data=campaign_data)

    async def delete_campaign_async(self, campaign_id: str) -> bool:
        """
        Delete campaign asynchronously.

        Args:
            campaign_id: Unique campaign identifier

        Returns:
            True if deletion successful
        """
        await self._make_request_async("DELETE", f"/campaigns/{campaign_id}")
        return True

    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete campaign synchronously."""
        self._make_request("DELETE", f"/campaigns/{campaign_id}")
        return True

    # Audience Targeting APIs

    async def get_audiences_async(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve audiences asynchronously.

        Args:
            limit: Maximum number of audiences to return
            offset: Number of audiences to skip
            filters: Optional filters for audiences

        Returns:
            Dict containing audience data and metadata
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return await self._make_request_async("GET", "/audiences", params=params)

    def get_audiences(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve audiences synchronously."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return self._make_request("GET", "/audiences", params=params)

    async def get_audience_async(self, audience_id: str) -> Dict[str, Any]:
        """
        Retrieve specific audience data asynchronously.

        Args:
            audience_id: Unique audience identifier

        Returns:
            Dict containing audience data
        """
        return await self._make_request_async("GET", f"/audiences/{audience_id}")

    def get_audience(self, audience_id: str) -> Dict[str, Any]:
        """Retrieve specific audience data synchronously."""
        return self._make_request("GET", f"/audiences/{audience_id}")

    async def create_audience_async(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new audience asynchronously.

        Args:
            audience_data: Audience definition data

        Returns:
            Dict containing created audience data
        """
        return await self._make_request_async("POST", "/audiences", data=audience_data)

    def create_audience(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new audience synchronously."""
        return self._make_request("POST", "/audiences", data=audience_data)

    async def update_audience_async(self, audience_id: str, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update audience definition asynchronously.

        Args:
            audience_id: Unique audience identifier
            audience_data: Updated audience data

        Returns:
            Dict containing updated audience data
        """
        return await self._make_request_async("PUT", f"/audiences/{audience_id}", data=audience_data)

    def update_audience(self, audience_id: str, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update audience definition synchronously."""
        return self._make_request("PUT", f"/audiences/{audience_id}", data=audience_data)

    async def delete_audience_async(self, audience_id: str) -> bool:
        """
        Delete audience asynchronously.

        Args:
            audience_id: Unique audience identifier

        Returns:
            True if deletion successful
        """
        await self._make_request_async("DELETE", f"/audiences/{audience_id}")
        return True

    def delete_audience(self, audience_id: str) -> bool:
        """Delete audience synchronously."""
        self._make_request("DELETE", f"/audiences/{audience_id}")
        return True

    async def estimate_audience_size_async(self, audience_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate audience size based on criteria asynchronously.

        Args:
            audience_criteria: Audience targeting criteria

        Returns:
            Dict containing audience size estimate
        """
        return await self._make_request_async("POST", "/audiences/estimate", data=audience_criteria)

    def estimate_audience_size(self, audience_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate audience size based on criteria synchronously."""
        return self._make_request("POST", "/audiences/estimate", data=audience_criteria)

    # Campaign Optimization APIs

    async def optimize_campaign_async(
        self,
        campaign_id: str,
        optimization_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize campaign performance asynchronously.

        Args:
            campaign_id: Unique campaign identifier
            optimization_params: Optional optimization parameters

        Returns:
            Dict containing optimization recommendations
        """
        payload = {
            "campaignId": campaign_id,
            "optimizationParams": optimization_params or {}
        }
        return await self._make_request_async("POST", "/campaigns/optimize", data=payload)

    def optimize_campaign(self, campaign_id: str, optimization_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize campaign performance synchronously."""
        payload = {
            "campaignId": campaign_id,
            "optimizationParams": optimization_params or {}
        }
        return self._make_request("POST", "/campaigns/optimize", data=payload)

    async def get_campaign_analytics_async(
        self,
        campaign_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get campaign analytics asynchronously.

        Args:
            campaign_id: Unique campaign identifier
            start_date: Start date for analytics (ISO format)
            end_date: End date for analytics (ISO format)

        Returns:
            Dict containing campaign analytics
        """
        params = {"campaignId": campaign_id}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        return await self._make_request_async("GET", "/analytics/campaigns", params=params)

    def get_campaign_analytics(
        self,
        campaign_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get campaign analytics synchronously."""
        params = {"campaignId": campaign_id}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        return self._make_request("GET", "/analytics/campaigns", params=params)

    # Campaign Templates APIs

    async def get_campaign_templates_async(
        self,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve campaign templates asynchronously.

        Args:
            category: Optional template category filter
            limit: Maximum number of templates to return
            offset: Number of templates to skip

        Returns:
            Dict containing campaign templates
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if category:
            params["category"] = category

        return await self._make_request_async("GET", "/templates/campaigns", params=params)

    def get_campaign_templates(
        self,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Retrieve campaign templates synchronously."""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if category:
            params["category"] = category

        return self._make_request("GET", "/templates/campaigns", params=params)

    async def create_campaign_from_template_async(self, template_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create campaign from template asynchronously.

        Args:
            template_id: Unique template identifier
            campaign_data: Campaign-specific configuration

        Returns:
            Dict containing created campaign data
        """
        payload = {
            "templateId": template_id,
            "campaignData": campaign_data
        }
        return await self._make_request_async("POST", "/campaigns/from-template", data=payload)

    def create_campaign_from_template(self, template_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create campaign from template synchronously."""
        payload = {
            "templateId": template_id,
            "campaignData": campaign_data
        }
        return self._make_request("POST", "/campaigns/from-template", data=payload)

    def __enter__(self):
        """Context manager entry."""
        if not self.validate_connection():
            raise CI360PlanningConnectionError("Failed to establish connection")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        if not await self.validate_connection_async():
            raise CI360PlanningConnectionError("Failed to establish connection")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.session.close()
