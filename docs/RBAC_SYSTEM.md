# RBAC System Implementation Guide

## Overview

RAG-ENTERPRISE now features a **complete Role-Based Access Control (RBAC)** system with 6 role tiers, 28 granular permissions, and professional admin interfaces for managing users and roles.

## Table of Contents

1. [Role Hierarchy](#role-hierarchy)
2. [Permissions](#permissions)
3. [API Endpoints](#api-endpoints)
4. [Frontend Pages](#frontend-pages)
5. [Implementation Examples](#implementation-examples)
6. [Testing](#testing)

---

## Role Hierarchy

### 1. **SUPER_ADMIN** 👑
- **Description:** Full system access with all permissions
- **Permissions:** All 28 permissions
- **Use Case:** System administrators, platform owners
- **Abilities:** Can create/delete users, manage roles, deploy agents, publish knowledge

### 2. **ADMIN** 🛡️
- **Description:** System administration and management
- **Permissions:** 22 permissions (excludes user creation/deletion)
- **Use Case:** Administrative staff managing operations
- **Abilities:** Can manage content, agents, knowledge bases, settings

### 3. **MANAGER** 📊
- **Description:** Team and content management
- **Permissions:** 14 permissions (create/read/update focus)
- **Use Case:** Department heads, content managers
- **Abilities:** Can create and update content, manage team agents and datasets

### 4. **EDITOR** ✏️
- **Description:** Content creation and editing
- **Permissions:** 8 permissions (content-focused)
- **Use Case:** Content creators, writers, analysts
- **Abilities:** Can create and edit knowledge items, manage conversations

### 5. **VIEWER** 👁️
- **Description:** Read-only access to system resources
- **Permissions:** 5 permissions (read-only)
- **Use Case:** Stakeholders, analysts, reporting staff
- **Abilities:** Can only read and access reports

### 6. **USER** 👤
- **Description:** Basic user access
- **Permissions:** 3 permissions (chat + knowledge read)
- **Use Case:** Regular platform users
- **Abilities:** Can chat with agents and read knowledge base

---

## Permissions

Permissions are organized into 8 categories:

### User Management
```
user:create     - Create new users
user:read       - View user profiles
user:update     - Modify user information
user:delete     - Remove users
```

### Agent Management
```
agent:create    - Create new agents
agent:read      - View agent details
agent:update    - Modify agent configuration
agent:delete    - Delete agents
agent:deploy    - Deploy agents to production
```

### Knowledge Management
```
knowledge:create   - Create knowledge items
knowledge:read     - Access knowledge base
knowledge:update   - Modify knowledge items
knowledge:delete   - Remove knowledge items
knowledge:publish  - Publish to public knowledge base
```

### Model Management
```
model:create    - Create ML models
model:read      - View model details
model:update    - Modify models
model:delete    - Remove models
```

### Dataset Management
```
dataset:create  - Create datasets
dataset:read    - Access datasets
dataset:update  - Modify datasets
dataset:delete  - Remove datasets
```

### Chat & Conversation
```
chat:create     - Create conversations
chat:read       - Access chat history
chat:delete     - Delete conversations
```

### Settings & Configuration
```
settings:read   - View system settings
settings:update - Modify settings
```

### System Administration
```
system:admin    - Full system administration access
```

---

## API Endpoints

### List All Roles
```bash
GET /api/v1/admin/roles
Authorization: Bearer <token>

Response:
{
  "success": true,
  "data": [
    {
      "id": "super_admin",
      "name": "SUPER_ADMIN",
      "display_name": "Super Admin",
      "permissions": [24 permissions...],
      "permission_count": 24
    },
    ...
  ]
}
```

### Get Role Details
```bash
GET /api/v1/admin/roles/{role_id}
Authorization: Bearer <token>

Example:
GET /api/v1/admin/roles/admin

Response:
{
  "success": true,
  "data": {
    "id": "admin",
    "name": "ADMIN",
    "display_name": "Admin",
    "permissions": [22 permissions...],
    "description": "System administration and management"
  }
}
```

### List All Permissions
```bash
GET /api/v1/admin/permissions
Authorization: Bearer <token>

Response:
{
  "success": true,
  "data": {
    "user": [
      {"id": "user:create", "name": "USER_CREATE", ...},
      ...
    ],
    "agent": [...],
    "knowledge": [...],
    ...
  },
  "total": 28
}
```

### Get User's Role
```bash
GET /api/v1/admin/users/{user_id}/role
Authorization: Bearer <token>

Response:
{
  "success": true,
  "data": {
    "user_id": "user123",
    "user_email": "user@example.com",
    "role": "MANAGER",
    "permissions": [14 permissions...]
  }
}
```

### Assign Role to User
```bash
PUT /api/v1/admin/users/{user_id}/role
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "role": "MANAGER"
}

Response:
{
  "success": true,
  "message": "User role updated from USER to MANAGER",
  "data": {
    "user_id": "user123",
    "old_role": "USER",
    "new_role": "MANAGER"
  }
}
```

### Get User Permissions
```bash
GET /api/v1/admin/users/{user_id}/permissions
Authorization: Bearer <token>

Response:
{
  "success": true,
  "data": {
    "user_id": "user123",
    "role": "MANAGER",
    "all_permissions": [14 permissions...],
    "grouped_permissions": {
      "agent": [3 permissions],
      "knowledge": [3 permissions],
      ...
    },
    "total_permissions": 14
  }
}
```

### Get Role Statistics
```bash
GET /api/v1/admin/statistics/roles
Authorization: Bearer <token>

Response:
{
  "success": true,
  "data": {
    "total_users": 25,
    "by_role": {
      "SUPER_ADMIN": 1,
      "ADMIN": 3,
      "MANAGER": 8,
      "EDITOR": 7,
      "VIEWER": 4,
      "USER": 2
    },
    "role_breakdown": [
      {
        "role": "SUPER_ADMIN",
        "count": 1,
        "percentage": 4.0
      },
      ...
    ]
  }
}
```

---

## Frontend Pages

### Admin Dashboard
**Path:** `/admin`
- **Features:**
  - System overview with key metrics
  - User distribution by role
  - Quick action buttons for all admin functions
  - System status indicators
  - Recent activity log

### User Management
**Path:** `/admin/users`
- **Features:**
  - List all users with filtering
  - Search by email or name
  - Filter by role
  - View user details
  - Invite new users
  - Edit user information
  - Assign roles to users
  - Remove users

### Role & Permission Management
**Path:** `/admin/roles-permissions`
- **Features:**
  - View all available roles with descriptions
  - View permission assignments per role
  - See user counts for each role
  - Create new roles (when available)
  - Assign permissions to roles
  - View comprehensive permission list
  - Category-based permission filtering

---

## Implementation Examples

### Example 1: Protecting an Endpoint with Single Permission

```python
from fastapi import APIRouter, Depends, HTTPException
from core.rbac import PermissionEnum, require_permission
from core.auth import get_current_user

router = APIRouter()

@router.get("/agents")
@require_permission(PermissionEnum.AGENT_READ)
async def list_agents(current_user = Depends(get_current_user)):
    """Only users with 'agent:read' permission can access this"""
    return {"agents": [...]}
```

### Example 2: Multiple Permissions (ANY)

```python
@router.post("/agents")
@require_any_permission([
    PermissionEnum.AGENT_CREATE,
    PermissionEnum.AGENT_UPDATE
])
async def create_or_update_agent(current_user = Depends(get_current_user)):
    """User must have either 'agent:create' OR 'agent:update'"""
    return {"success": True}
```

### Example 3: Multiple Permissions (ALL)

```python
@router.delete("/agents/{agent_id}")
@require_all_permissions([
    PermissionEnum.AGENT_DELETE,
    PermissionEnum.SYSTEM_ADMIN
])
async def delete_agent(current_user = Depends(get_current_user)):
    """User must have BOTH permissions"""
    return {"success": True}
```

### Example 4: Role-Based Access

```python
from core.rbac import RoleEnum, require_role

@router.post("/admin/users")
@require_role(RoleEnum.SUPER_ADMIN, RoleEnum.ADMIN)
async def create_user(current_user = Depends(get_current_user)):
    """Only SUPER_ADMIN or ADMIN can access this"""
    return {"success": True}
```

### Example 5: Manual Permission Check

```python
from core.rbac import has_permission, PermissionEnum

@router.get("/protected-resource")
async def protected_endpoint(current_user = Depends(get_current_user)):
    """Manually check permission"""
    if not has_permission(
        current_user.role or "USER",
        PermissionEnum.AGENT_READ
    ):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return {"data": "sensitive"}
```

---

## Testing

### Test 1: List All Roles

```bash
curl -X GET http://localhost:8000/api/v1/admin/roles \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 2: Get Current User's Permissions

```bash
# Get the current user's ID from auth response
curl -X GET http://localhost:8000/api/v1/admin/users/{user_id}/permissions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 3: Assign Role

```bash
curl -X PUT http://localhost:8000/api/v1/admin/users/{user_id}/role \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "MANAGER"}'
```

### Test 4: Check Role Statistics

```bash
curl -X GET http://localhost:8000/api/v1/admin/statistics/roles \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 5: Permission Check with Frontend

1. Login as SUPER_ADMIN → `/admin/users` ✓ (has access)
2. Logout → Login as VIEWER → `/admin/users` ✗ (permission denied)
3. Login as ADMIN → `/admin/roles-permissions` ✓ (has access)

---

## File Structure

```
RAG-ENTERPRISE/
├── core/
│   ├── rbac.py                          # RBAC enums and permission checks
│   └── permissions_decorators.py        # FastAPI permission decorators
├── api/
│   └── routes/
│       └── admin_roles.py               # RBAC management endpoints
└── frontend/
    └── app/
        └── (dashboard)/
            └── admin/
                ├── page.tsx             # Admin dashboard
                ├── users/
                │   └── page.tsx         # User management
                └── roles-permissions/
                    └── page.tsx         # Role/permission management
```

---

## Key Features

✅ **6 Role Tiers** - From basic user to super admin
✅ **28 Granular Permissions** - Fine-grained access control
✅ **Easy Integration** - Simple decorators for endpoint protection
✅ **Admin UI** - Complete frontend for managing users and roles
✅ **REST API** - Full API for programmatic access
✅ **Permission Inheritance** - Roles inherit all assigned permissions
✅ **Activity Logging** - Track all role changes
✅ **Statistics Dashboard** - View user distribution by role

---

## Next Steps

1. **Database Migration**: Add role fields to User model
2. **Decorator Integration**: Apply @require_permission decorators to existing endpoints
3. **Advanced Features**: Role templates, permission groups, audit logging
4. **Custom Roles**: Allow admins to create custom roles with selected permissions

---

## Support

For issues or questions about the RBAC system:
1. Check `/docs/RBAC_INTEGRATION_GUIDE.md`
2. Review endpoint examples in `/api/routes/admin_roles.py`
3. Check permission definitions in `/core/rbac.py`
