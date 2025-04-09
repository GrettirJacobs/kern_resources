# Token Tracker: Next Development Steps

## Priority Task: Align Database Schema

Based on our analysis, the most critical issue to address is the mismatch between the database schema used in tests and the actual implementation. This is causing several tests to be skipped and could lead to issues when deploying the system.

### Detailed Implementation Plan

#### 1. Update Database Models

1. **Modify the `BudgetAlert` model to include the `slack_webhook` column**:
   - Add a `slack_webhook` column to the `BudgetAlert` model in `database/models.py`
   - Make it nullable to maintain backward compatibility
   - Add appropriate documentation

2. **Ensure the `TokenUsage` model includes the `user_id` column**:
   - Verify that the `user_id` column is properly defined in the `TokenUsage` model
   - Make it nullable to maintain backward compatibility
   - Add appropriate documentation

#### 2. Create Database Migrations

1. **Set up Alembic for database migrations**:
   - Initialize Alembic in the project if not already done
   - Configure Alembic to work with the SQLAlchemy models

2. **Create a migration script for the schema changes**:
   - Generate a migration script to add the missing columns
   - Test the migration script on a test database
   - Document the migration process

#### 3. Update Test Fixtures

1. **Modify the test database setup**:
   - Update the `test_db` fixture in `tests/conftest.py` to create tables with the correct schema
   - Ensure all test fixtures are compatible with the updated schema

2. **Fix skipped tests**:
   - Remove the `@pytest.mark.skip` decorators from the skipped tests
   - Update the tests to work with the new schema
   - Run the tests to verify they pass

#### 4. Update Documentation

1. **Update the README.md file**:
   - Document the schema changes
   - Update the installation and migration instructions

2. **Update code-level documentation**:
   - Add docstrings to the new columns
   - Update any affected method documentation

### Implementation Details

#### BudgetAlert Model Changes

```python
class BudgetAlert(Base):
    """
    Model for storing budget alert configurations.
    """
    __tablename__ = "budget_alerts"

    id = Column(Integer, primary_key=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    threshold = Column(Float, nullable=False)  # Percentage (0-100)
    email = Column(String(100), nullable=True)
    slack_webhook = Column(String(200), nullable=True)  # New column for Slack notifications
    triggered = Column(Boolean, default=False)
    last_triggered = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    budget = relationship("Budget", back_populates="alerts")

    def __repr__(self):
        return f"<BudgetAlert(budget_id={self.budget_id}, threshold={self.threshold})>"
```

#### TokenUsage Model Verification

The `TokenUsage` model already includes the `user_id` column, but we need to ensure it's properly defined and documented:

```python
class TokenUsage(Base):
    """
    Model for storing token usage data.
    """
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True)
    request_id = Column(String(36), nullable=False)  # UUID
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    model = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    user_id = Column(String(100), nullable=True)  # User ID for tracking usage by user
    endpoint = Column(String(100), nullable=True)
    status = Column(String(20), nullable=True)
    latency = Column(Float, nullable=True)  # in seconds
    request_metadata = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<TokenUsage(request_id={self.request_id}, model={self.model}, total_tokens={self.total_tokens})>"
```

#### Alembic Migration Script

```python
"""Add slack_webhook column to budget_alerts table

Revision ID: abcdef123456
Revises: previous_revision_id
Create Date: 2025-04-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'abcdef123456'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None


def upgrade():
    # Add slack_webhook column to budget_alerts table
    op.add_column('budget_alerts', sa.Column('slack_webhook', sa.String(200), nullable=True))


def downgrade():
    # Remove slack_webhook column from budget_alerts table
    op.drop_column('budget_alerts', 'slack_webhook')
```

### Testing Strategy

1. **Unit Tests**:
   - Update unit tests for the `BudgetAlert` model to test the new `slack_webhook` column
   - Verify that the `TokenUsage` model tests properly handle the `user_id` column

2. **Integration Tests**:
   - Update integration tests to use the new schema
   - Test the interaction between components with the updated schema

3. **Migration Tests**:
   - Test the migration script on a test database
   - Verify that existing data is preserved during migration

### Expected Outcomes

1. **All tests passing**: The skipped tests should now pass with the updated schema
2. **Improved code quality**: The codebase will be more consistent with better documentation
3. **Better maintainability**: The migration scripts will make it easier to update the schema in the future
4. **Enhanced features**: The `slack_webhook` column will enable Slack notifications in a future update

### Timeline

- **Database Model Updates**: 1 day
- **Migration Script Creation**: 1 day
- **Test Fixture Updates**: 1 day
- **Documentation Updates**: 1 day
- **Testing and Validation**: 1 day

Total estimated time: **5 days**

### Risks and Mitigations

1. **Risk**: Migration fails on production database
   - **Mitigation**: Test the migration thoroughly on a staging database before applying to production
   - **Mitigation**: Create a backup of the production database before migration

2. **Risk**: Updated schema breaks existing functionality
   - **Mitigation**: Ensure all columns are nullable to maintain backward compatibility
   - **Mitigation**: Add comprehensive tests for all affected components

3. **Risk**: Performance impact of schema changes
   - **Mitigation**: Monitor database performance before and after the changes
   - **Mitigation**: Optimize queries if necessary

### Conclusion

Aligning the database schema is a critical first step in stabilizing the Token Tracker system. By addressing the schema mismatches, we can fix the skipped tests and ensure that all components work together correctly. This will provide a solid foundation for future development and make it easier to add new features like Slack notifications.
