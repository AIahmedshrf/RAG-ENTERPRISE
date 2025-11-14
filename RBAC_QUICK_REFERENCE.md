# 🔐 RBAC System - Quick Reference Card

## Roles at a Glance

```
SUPER_ADMIN  →  28 perms  →  Platform owner
ADMIN        →  21 perms  →  System admin
MANAGER      →  12 perms  →  Team manager
EDITOR       →   8 perms  →  Content creator
VIEWER       →   6 perms  →  Read-only user
USER         →   3 perms  →  Basic access
```

## Common Permissions

| Permission | Use Case |
|-----------|----------|
| `agent:create` | Create AI agents |
| `agent:read` | View agent details |
| `knowledge:create` | Create knowledge items |
| `knowledge:publish` | Publish to public KB |
| `user:create` | Create new users |
| `user:read` | View user profiles |
| `chat:create` | Start conversations |
| `settings:update` | Change system settings |

## API Endpoints

```bash
# List roles
GET /api/v1/admin/roles

# Get user's role
GET /api/v1/admin/users/{user_id}/role

# Assign role
PUT /api/v1/admin/users/{user_id}/role
# { "role": "MANAGER" }

# Get user's permissions
GET /api/v1/admin/users/{user_id}/permissions

# Role statistics
GET /api/v1/admin/statistics/roles
```

## Frontend Pages

```
/admin                    - Dashboard
/admin/users             - User management
/admin/roles-permissions - Role & permission management
```

## Protect an Endpoint

```python
from core.rbac import PermissionEnum, require_permission

@app.get("/agents")
@require_permission(PermissionEnum.AGENT_READ)
async def list_agents(current_user = Depends(get_current_user)):
    return {"agents": [...]}
```

## Check Permission in Code

```python
from core.rbac import has_permission, PermissionEnum

if has_permission(user.role, PermissionEnum.AGENT_DELETE):
    delete_agent(agent_id)
```

## Test the System

```bash
cd /workspaces/RAG-ENTERPRISE
python test_rbac_system.py
```

## Files

- **Core**: `core/rbac.py`, `core/permissions_decorators.py`
- **API**: `api/routes/admin_roles.py`
- **UI**: `/admin/users`, `/admin/roles-permissions`
- **Docs**: `docs/RBAC_SYSTEM.md`

## Quick Stats

- **6** Roles
- **28** Permissions
- **8** Categories
- **7** API Endpoints
- **3** Admin Pages
- **600+** Lines Documentation

---

**Status**: ✅ Production Ready | **Build**: ✅ Passing | **Tests**: ✅ All Pass
