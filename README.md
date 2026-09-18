# SAS Customer Intelligence 360

## SAS 360 SOLUTIONS - Planning Module

This repository provides Python interfaces for SAS Customer Intelligence 360 Planning APIs.

### Overview

The Planning module enables programmatic management of marketing plans, campaigns, and strategic planning within CI360.

### Features

- Marketing plan creation and management
- Campaign planning and scheduling
- Budget and resource allocation
- Plan execution tracking
- Performance analytics

### Prerequisites

- Python 3.8+
- Access to SAS Customer Intelligence 360 environment
- Required dependencies (see requirements.txt)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mnelson3/sas-ci360-sol-planning.git
   cd sas-ci360-sol-planning
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Getting Started

```python
from sasci360solplanning import CI360PlanningBase, CI360PlanningConfig

# Configure the planning client
config = CI360PlanningConfig(
    algorithm="HS256",
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id"
)

# Initialize planning client
planning_client = CI360PlanningBase(config)

# Create and manage marketing plans
```

### Solutions Code

The planning module provides:

1. **Plan Management**: Create and modify marketing plans
2. **Campaign Planning**: Design and schedule campaigns
3. **Resource Allocation**: Budget and resource management
4. **Performance Tracking**: Monitor plan execution and ROI

### Troubleshooting

- Verify plan configurations and hierarchies
- Check scheduling conflicts
- Review budget constraints
- Monitor plan execution status

## 🛠️ Developer/Implementation Guide

This section provides comprehensive guidance for developers implementing marketing planning solutions with SAS CI360.

### Architecture Overview

The SAS CI360 Planning module follows a hierarchical planning architecture designed for strategic marketing management:

```
┌─────────────────────────────────────────────────────────────┐
│                  Planning Module                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Plan        │ │ Campaign    │ │ Resource    │           │
│  │ Management  │ │ Planning    │ │ Allocation  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ REST API    │ │ JWT Auth    │ │ Async I/O   │           │
│  │ Client      │ │ & Security  │ │ Operations  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

#### Core Components

1. **Plan Management Layer**
   - `CI360PlanningBase`: Core client class for planning operations
   - Marketing plan lifecycle management
   - Plan hierarchy and dependencies
   - Strategic objective alignment

2. **Campaign Planning Layer**
   - Campaign design and scheduling
   - Target audience planning
   - Channel strategy development
   - Timeline and milestone management

3. **Resource Allocation Layer**
   - Budget planning and tracking
   - Resource assignment and optimization
   - ROI forecasting and analysis
   - Performance measurement

### Configuration Management

#### Environment Variables
```bash
export SAS_CI360_SECRET_KEY="your-secret-key"
export SAS_CI360_TENANT_ID="your-tenant-id"
```

#### Configuration Class
```python
from sasci360solplanning.base import CI360PlanningConfig

config = CI360PlanningConfig(
    algorithm="HS256",
    api="plan",
    encoding="utf-8",
    host="your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id"
)
```

### API Integration Patterns

#### Marketing Plan Management
```python
from sasci360solplanning.base import CI360PlanningBase

# Initialize client
client = CI360PlanningBase()

# Create a marketing plan
plan_data = {
    'name': 'Q4 2024 Marketing Plan',
    'description': 'Comprehensive holiday marketing strategy',
    'objectives': [
        'Increase revenue by 25%',
        'Acquire 10,000 new customers',
        'Improve brand awareness'
    ],
    'budget': {
        'total': 500000,
        'currency': 'USD',
        'allocation': {
            'digital': 0.4,
            'traditional': 0.3,
            'events': 0.3
        }
    },
    'timeline': {
        'start_date': '2024-10-01',
        'end_date': '2024-12-31'
    }
}

result = client.create_plan(plan_data)
print(f"Plan created: {result['plan_id']}")
```

#### Asynchronous Operations
```python
import asyncio
from sasci360solplanning.base import CI360PlanningBase

async def manage_marketing_plan():
    client = CI360PlanningBase()

    # Get plan details asynchronously
    plan = await client.get_plan_async('plan-123')
    print(f"Plan: {plan['name']} - Budget: ${plan['budget']['total']}")

    # Update plan with new objectives
    update_data = {
        'objectives': plan['objectives'] + ['Launch new product line'],
        'budget': {
            'total': 600000,
            'allocation': {
                'digital': 0.5,
                'traditional': 0.2,
                'events': 0.2,
                'product_launch': 0.1
            }
        }
    }
    result = await client.update_plan_async('plan-123', update_data)
    print(f"Plan updated: {result['plan_id']}")

# Run async operations
asyncio.run(manage_marketing_plan())
```

#### Campaign Planning
```python
# Create campaign within a plan
campaign_data = {
    'plan_id': 'plan-123',
    'name': 'Holiday Email Campaign',
    'description': 'Seasonal email marketing campaign',
    'channels': ['email', 'social_media'],
    'target_audience': {
        'segments': ['newsletter_subscribers', 'past_customers'],
        'size': 50000
    },
    'budget': 75000,
    'schedule': {
        'start_date': '2024-11-01T09:00:00Z',
        'end_date': '2024-12-24T23:59:59Z'
    },
    'goals': {
        'open_rate_target': 0.25,
        'click_rate_target': 0.05,
        'conversion_target': 0.02
    }
}

campaign = client.create_campaign(campaign_data)
print(f"Campaign created: {campaign['campaign_id']}")
```

### Error Handling

#### Exception Types
```python
from sasci360solplanning.base import (
    CI360PlanningBase,
    CI360PlanningError,
    CI360PlanningAuthError,
    CI360PlanningValidationError
)

try:
    client = CI360PlanningBase()
    plans = client.get_plans()
except CI360PlanningAuthError as e:
    print(f"Authentication failed: {e}")
    # Handle auth issues (token refresh, credentials)
except CI360PlanningValidationError as e:
    print(f"Validation error: {e}")
    # Handle plan/campaign validation issues
except CI360PlanningError as e:
    print(f"Planning error: {e}")
    # Handle general planning API errors
```

#### Plan Validation
```python
def validate_plan_data(plan_data):
    """Validate plan data before submission"""
    errors = []

    if not plan_data.get('name'):
        errors.append("Plan name is required")

    if not plan_data.get('budget', {}).get('total'):
        errors.append("Total budget is required")

    timeline = plan_data.get('timeline', {})
    if not timeline.get('start_date') or not timeline.get('end_date'):
        errors.append("Timeline start and end dates are required")

    # Check budget allocation sums to 1.0
    allocation = plan_data.get('budget', {}).get('allocation', {})
    if allocation and abs(sum(allocation.values()) - 1.0) > 0.001:
        errors.append("Budget allocation percentages must sum to 100%")

    return errors

# Usage
plan_data = {...}  # Your plan data
errors = validate_plan_data(plan_data)
if errors:
    print("Plan validation failed:")
    for error in errors:
        print(f"  - {error}")
else:
    result = client.create_plan(plan_data)
```

### Testing Approaches

#### Unit Testing
```python
import unittest
from unittest.mock import Mock, patch
from sasci360solplanning.base import CI360PlanningBase

class TestPlanningOperations(unittest.TestCase):
    def setUp(self):
        self.client = CI360PlanningBase()
        self.mock_response = Mock()
        self.mock_response.json.return_value = {'plan_id': '123', 'status': 'created'}

    @patch('requests.Session.request')
    def test_create_plan(self, mock_request):
        mock_request.return_value = self.mock_response

        result = self.client.create_plan({'name': 'Test Plan'})
        self.assertEqual(result['status'], 'created')
        mock_request.assert_called_once()

    @patch('sasci360solplanning.base.CI360PlanningBase._generate_token')
    def test_planning_authentication(self, mock_generate):
        mock_generate.return_value = 'mock-jwt-token'

        headers = self.client.get_auth_headers()
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], 'Bearer mock-jwt-token')
```

#### Integration Testing
```python
import pytest
from sasci360solplanning.base import CI360PlanningBase

@pytest.fixture
def planning_client():
    return CI360PlanningBase()

@pytest.mark.integration
def test_plan_lifecycle(planning_client):
    # Test complete plan lifecycle
    plan_data = {
        'name': 'Integration Test Plan',
        'description': 'Test plan for integration testing',
        'budget': {'total': 10000, 'currency': 'USD'},
        'timeline': {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
    }

    # Create
    created = planning_client.create_plan(plan_data)
    plan_id = created['plan_id']

    # Read
    retrieved = planning_client.get_plan(plan_id)
    assert retrieved['name'] == 'Integration Test Plan'

    # Update
    updated_data = plan_data.copy()
    updated_data['description'] = 'Updated description'
    updated = planning_client.update_plan(plan_id, updated_data)
    assert updated['description'] == 'Updated description'

    # Delete
    deleted = planning_client.delete_plan(plan_id)
    assert deleted is True
```

### Performance Considerations

#### Hierarchical Plan Processing
```python
# Process plans with dependencies
def process_plan_hierarchy(client, root_plan_id):
    """Process plans in hierarchical order respecting dependencies"""
    processed = set()
    queue = [root_plan_id]

    while queue:
        plan_id = queue.pop(0)
        if plan_id in processed:
            continue

        plan = client.get_plan(plan_id)

        # Check if dependencies are processed
        dependencies = plan.get('dependencies', [])
        if all(dep in processed for dep in dependencies):
            # Process this plan
            process_plan(plan)
            processed.add(plan_id)

            # Add child plans to queue
            child_plans = plan.get('child_plans', [])
            queue.extend(child_plans)
        else:
            # Re-queue for later processing
            queue.append(plan_id)
```

#### Budget Optimization
```python
# Optimize budget allocation across campaigns
def optimize_budget_allocation(client, plan_id, total_budget, constraints):
    """Optimize budget allocation using linear programming"""
    campaigns = client.get_plan_campaigns(plan_id)

    # Define optimization problem
    # This is a simplified example - use libraries like PuLP or scipy.optimize
    # for production implementations

    allocations = {}
    remaining_budget = total_budget

    for campaign in campaigns:
        # Calculate optimal allocation based on constraints
        base_allocation = campaign['estimated_cost']
        efficiency_factor = campaign.get('efficiency_score', 1.0)

        allocation = min(
            base_allocation * efficiency_factor,
            remaining_budget * constraints.get('max_per_campaign', 0.3)
        )

        allocations[campaign['id']] = allocation
        remaining_budget -= allocation

    return allocations
```

#### Forecasting and Analytics
```python
# Generate plan performance forecasts
def forecast_plan_performance(client, plan_id, historical_data):
    """Generate performance forecasts using historical data"""
    plan = client.get_plan(plan_id)
    campaigns = client.get_plan_campaigns(plan_id)

    forecast = {
        'revenue_projection': 0,
        'customer_acquisition': 0,
        'roi_estimate': 0
    }

    for campaign in campaigns:
        # Use historical performance data for forecasting
        historical_performance = historical_data.get(campaign['type'], {})
        conversion_rate = historical_performance.get('conversion_rate', 0.02)
        avg_order_value = historical_performance.get('avg_order_value', 50)

        projected_conversions = campaign['target_audience_size'] * conversion_rate
        projected_revenue = projected_conversions * avg_order_value

        forecast['revenue_projection'] += projected_revenue
        forecast['customer_acquisition'] += projected_conversions

    if plan['budget']['total'] > 0:
        forecast['roi_estimate'] = forecast['revenue_projection'] / plan['budget']['total']

    return forecast
```

### Strategic Planning Best Practices

1. **Objective Alignment**: Ensure all plans align with business objectives
2. **Resource Optimization**: Use data-driven budget allocation
3. **Risk Management**: Implement contingency planning for campaigns
4. **Performance Monitoring**: Continuous tracking and adjustment
5. **Stakeholder Communication**: Regular reporting and updates

### Contributing

We welcome your contributions! Please read [CONTRIBUTING](CONTRIBUTING.md) for details on how to submit contributions to this project.

### License

This project is licensed under the [Nelson Grey LLC Community License 1.0](LICENSE).

- **Free for individuals, education, and research**: use, modify, and distribute this software for non-commercial purposes
- **Commercial evaluation**: evaluate the software for a possible commercial use, free of charge
- **Commercial production use**: requires a commercial license from Nelson Grey LLC
- **Automatic conversion**: on December 13, 2029, this automatically converts to the Apache License 2.0

For commercial licensing inquiries, contact support@nelsongrey.com.

### Additional Resources

For more information, see [Plan API](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/rest-plan-api.htm).
