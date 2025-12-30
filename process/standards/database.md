# Database Development Guidelines for LLM Agents

## Overview
This document provides comprehensive guidelines for LLM agents working with database creation, schema management, and data persistence in the Taxiway project. Follow these practices to ensure consistency, maintainability, and optimal performance.

## Core Principles

### 1. Dual-Layer Architecture
- **SQLAlchemy Models**: Define database schema and relationships in `models.py` files
- **Pydantic Schemas**: Define data validation, serialization, and business logic in `schemas.py` files
- **Separation of Concerns**: Keep database concerns in models, business logic in schemas

### 2. PostgreSQL 15+ Features
- Use PostgreSQL-specific features and optimizations
- Leverage JSONB for flexible data storage
- Utilize UUID types for primary keys
- Implement proper indexing strategies
- Use PostgreSQL 15+ specific functions and operators

### 3. Migration Strategy
- **DO NOT** run `alembic upgrade head` directly on production databases
- **DO** generate DDL scripts in offline mode using `alembic upgrade --sql`
- **DO** review and manually apply DDL scripts to production
- **DO** use alembic for development and staging environments

## Model Development Guidelines

### Base Classes
All persistent models MUST inherit from the appropriate base class:

```python
# For standard models with audit fields
class MyModel(Base):
    pass

# For models requiring JSON data storage
class MyJsonModel(Base, JsonBase):
    pass
```

### Required Fields
All models inherit these audit fields from `Base`:
- `created_at`: Timestamp with timezone (auto-populated)
- `updated_at`: Timestamp with timezone (auto-populated) 
- `deleted_at`: Soft delete timestamp (nullable)
- `version`: Optimistic locking version (auto-incremented)

### Primary Keys
- **ALWAYS** use UUID primary keys
- Use the custom `UUIDType` for cross-database compatibility
- Generate UUIDs using `uuid.uuid4()` as default

```python
from taxiway.models import UUIDType
import uuid

class MyModel(Base):
    my_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4
    )
```

### Data Types
- **JSON Data**: Use `JsonType` for flexible data storage (automatically uses JSONB in PostgreSQL)
- **Text Fields**: Use `String` for short text, `UnicodeText` for long text
- **Timestamps**: Always use `DateTime(timezone=True)` for timezone-aware timestamps
- **Arrays**: Use PostgreSQL `ARRAY` type for array fields
- **Vectors**: Use `pgvector.VECTOR` for embedding storage

### Indexing Strategy
- **ALWAYS** create indexes for foreign keys
- **ALWAYS** create indexes for frequently queried fields
- **ALWAYS** create indexes for `version` field (inherited from Base)
- **CONSIDER** composite indexes for multi-column queries
- **USE** partial indexes for soft-deleted records

```python
from sqlalchemy import Index

class MyModel(Base):
    # ... fields ...
    
    __table_args__ = (
        Index('ix_mymodel_customer_status', 'customer_id', 'status'),
        Index('ix_mymodel_active', 'status', postgresql_where=deleted_at.is_(None)),
    )
```

### Relationships
- **DO NOT** Use explicit foreign key constraints
- **DO NOT** Define proper cascade behaviors
- **DO NOT** Use `back_populates` for bidirectional relationships
- **DO NOT** Consider lazy loading strategies

## Schema Development Guidelines

### Pydantic Integration
- Create corresponding Pydantic schemas for all models
- Use Pydantic for data validation and serialization
- Implement proper field validation and constraints
- Use Pydantic's `Field` for metadata and validation

```python
from pydantic import BaseModel, Field
from typing import Optional
import uuid

class CustomerSchema(BaseModel):
    customer_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    version: int = Field(..., ge=1)
```

### Business Logic
- Keep business logic in Pydantic schemas, not in SQLAlchemy models
- Use Pydantic validators for complex validation rules
- Implement data transformation methods in schemas
- Use Pydantic's `@field_validator` for custom validation

### API Integration
- Create separate schemas for API requests and responses
- Use inheritance to avoid duplication
- Implement proper error handling and validation messages

## Migration Management

### Creating Migrations
1. **Modify Models**: Update SQLAlchemy models in `models.py` files
2. **Generate Migration**: Run `alembic revision --autogenerate -m "description"`
3. **Review Migration**: Always review auto-generated migrations
4. **Test Migration**: Test on development database first

### Migration Best Practices
- **NEVER** modify existing migration files after they've been applied
- **ALWAYS** provide meaningful migration descriptions
- **REVIEW** auto-generated migrations for correctness
- **TEST** migrations on sample data before production
- **BACKUP** database before applying migrations

### Offline DDL Generation
For production deployments, generate DDL scripts:

```bash
# Generate SQL script without applying
alembic upgrade --sql head

# Generate SQL script for specific revision
alembic upgrade --sql <revision_id>
```
## Performance Considerations

### Query Optimization
- Use proper indexing strategies
- Implement query result caching where appropriate
- Use database-level constraints for data integrity
- Consider read replicas for read-heavy workloads

### Connection Management
- Use connection pooling
- Implement proper session management
- Use the Unit of Work pattern for transaction management
- Handle connection timeouts gracefully

### Data Volume
- Implement pagination for large result sets
- Use soft deletes instead of hard deletes when possible
- Consider data archiving strategies
- Monitor query performance and optimize as needed

## Security Guidelines

### Data Protection
- Use parameterized queries (SQLAlchemy handles this)
- Implement proper access controls
- Encrypt sensitive data at rest
- Use database-level encryption for sensitive fields

### Audit Trail
- Leverage the built-in audit fields (`created_at`, `updated_at`, `version`)
- Implement change tracking for critical data
- Use soft deletes to maintain data history
- Log database access and modifications

## Testing Guidelines

### Unit Tests
- Test model relationships and constraints
- Test Pydantic schema validation
- Test business logic in schemas
- Use test database for all tests

### Integration Tests
- Test database migrations
- Test full data flow from API to database
- Test error handling and edge cases
- Use fixtures for test data setup

### Test Database Setup
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from taxiway.models import Base

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

## Common Patterns

### Soft Delete Implementation
```python
class MyModel(Base):
    # ... other fields ...
    
    def soft_delete(self):
        self.deleted_at = datetime.now(timezone.utc)
    
    @classmethod
    def active_records(cls, session):
        return session.query(cls).filter(cls.deleted_at.is_(None))
```

### Optimistic Locking
```python
# The Base class already implements optimistic locking via version field
# Use it in your update operations:

def update_model(session, model_id, data):
    model = session.query(MyModel).filter(MyModel.id == model_id).first()
    if not model:
        raise EntityNotFoundException()
    
    # Update fields
    for key, value in data.items():
        setattr(model, key, value)
    
    try:
        session.commit()
    except StaleDataError:
        session.rollback()
        raise OptimisticLockError()
```

### JSON Data Handling
```python
class MyJsonModel(Base, JsonBase):
    # Inherits data field from JsonBase
    
    def set_data(self, key: str, value: Any):
        if not self.data:
            self.data = {}
        self.data[key] = value
        # Mark the field as modified for SQLAlchemy
        flag_modified(self, 'data')
```

## Error Handling

### Database Exceptions
- Handle `IntegrityError` for constraint violations
- Handle `StaleDataError` for optimistic locking conflicts
- Handle `OperationalError` for connection issues
- Implement proper rollback strategies

### Custom Exceptions
```python
from taxiway.exceptions import (
    EntityNotFoundException,
    DuplicateEntityException,
    OptimisticLockError,
    IllegalArgumentException
)
```

## Documentation Requirements

### Model Documentation
- Document all model relationships
- Explain complex business rules
- Document performance considerations
- Include usage examples

### Schema Documentation
- Document validation rules
- Explain data transformations
- Document API usage patterns
- Include error handling examples

## Checklist for Database Changes

Before implementing any database changes, ensure:

- [ ] Model inherits from appropriate base class
- [ ] All required audit fields are present
- [ ] Primary key uses UUID type
- [ ] Proper indexes are defined
- [ ] Relationships are properly configured
- [ ] Corresponding Pydantic schemas exist
- [ ] Migration is generated and reviewed
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] Performance implications are considered
- [ ] Security implications are reviewed

## Anti-Patterns to Avoid

### DO NOT:
- Use hard-coded strings for table/column names
- Skip index creation for foreign keys
- Use raw SQL without proper escaping
- Modify existing migration files
- Run alembic upgrade directly on production
- Ignore database constraints
- Use synchronous operations for bulk data operations
- Store sensitive data without encryption
- Skip validation in Pydantic schemas
- Use database-specific features without abstraction

### DO NOT:
- Create circular dependencies between models
- Use eager loading for all relationships
- Skip transaction management
- Ignore connection pooling
- Use database as a message queue
- Store large binary data in database
- Skip backup before migrations
- Use database for session storage without encryption
- Ignore query performance monitoring
- Skip error handling in database operations

## Conclusion

Following these guidelines ensures:
- Consistent database design across the application
- Proper separation of concerns between models and schemas
- Safe and reliable database migrations
- Optimal performance and security
- Maintainable and testable code

Always prioritize data integrity, performance, and security when making database-related decisions.

**Database Guidelines Compliance Checklist**:
- [ ] Models inherit from appropriate base class (Base or Base + JsonBase)
- [ ] All required audit fields are present (created_at, updated_at, deleted_at, version)
- [ ] Primary keys use UUIDType with uuid.uuid4() default
- [ ] Proper indexes are defined for frequently queried fields
- [ ] **NO** foreign key constraints or relationships are defined
- [ ] Corresponding Pydantic schemas exist with business logic validation
- [ ] Migration is generated using `alembic revision --autogenerate`
- [ ] Offline DDL script is generated for production using `alembic upgrade --sql`
- [ ] **NO** direct `alembic upgrade head` on production databases
- [ ] PostgreSQL 15+ features are utilized (JSONB, proper indexing)
- [ ] Soft delete methods use inherited deleted_at field
- [ ] Business logic is in Pydantic schemas, not SQLAlchemy models