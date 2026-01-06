# 📚 Database Migrations Guide

## Alembic Setup

Alembic has been configured for database migrations.

### Initial Setup

1. **Create initial migration:**
```bash
alembic revision --autogenerate -m "Initial migration"
```

2. **Apply migrations:**
```bash
alembic upgrade head
```

### Common Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

### Important Notes

- Migrations are stored in `alembic/versions/`
- Always review auto-generated migrations before applying
- Test migrations on a development database first
- Keep migrations small and focused

---

**Note:** The project currently uses `Base.metadata.create_all()` in `main.py` for development. For production, use Alembic migrations instead.

