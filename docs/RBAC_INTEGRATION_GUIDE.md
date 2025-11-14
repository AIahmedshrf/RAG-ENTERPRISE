"""
Integration Guide for RBAC Permissions in FastAPI Routes

This file provides examples of how to use the permission decorators
and role-based access control throughout the application.
"""

# ==================== EXAMPLE 1: Simple Permission Check ====================
"""
@router.get("/agents")
@require_permission(PermissionEnum.AGENT_READ)
async def list_agents(current_user: User = Depends(get_current_user)):
    # This route is now protected - only users with 'agent:read' permission can access it
    return {"agents": [...]}
"""

# ==================== EXAMPLE 2: Multiple Permissions (ANY) ====================
"""
@router.post("/agents")
@require_any_permission([PermissionEnum.AGENT_CREATE, PermissionEnum.AGENT_UPDATE])
async def create_or_update_agent(current_user: User = Depends(get_current_user)):
    # User must have either 'agent:create' OR 'agent:update' permission
    return {"success": True}
"""

# ==================== EXAMPLE 3: Multiple Permissions (ALL) ====================
"""
@router.delete("/agents/{agent_id}")
@require_all_permissions([PermissionEnum.AGENT_DELETE, PermissionEnum.SYSTEM_ADMIN])
async def delete_agent(current_user: User = Depends(get_current_user)):
    # User must have BOTH 'agent:delete' AND 'system:admin' permissions
    return {"success": True}
"""

# ==================== EXAMPLE 4: Role-Based Access ====================
"""
@router.post("/admin/users")
@require_role(RoleEnum.SUPER_ADMIN, RoleEnum.ADMIN)
async def create_user(current_user: User = Depends(get_current_user)):
    # Only SUPER_ADMIN or ADMIN roles can access this
    return {"success": True}
"""

# ==================== EXAMPLE 5: Using Helper Functions ====================
"""
from core.rbac import has_permission, RoleEnum, PermissionEnum

@router.get("/protected-resource")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    # Manual check using helper function
    if not has_permission(current_user.role or "USER", PermissionEnum.AGENT_READ):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return {"data": "sensitive"}
"""

# ==================== PERMISSION HIERARCHY ====================
"""
Role Hierarchy (from most to least privileged):
1. SUPER_ADMIN    - All 24 permissions
2. ADMIN          - 22 permissions (cannot create/delete users directly)
3. MANAGER        - 14 permissions (create/read/update only)
4. EDITOR         - 8 permissions (content focused)
5. VIEWER         - 5 permissions (read-only)
6. USER           - 3 permissions (basic chat + knowledge read)

Permission Categories:
- user:*          - User management (create, read, update, delete)
- agent:*         - Agent management (create, read, update, delete, deploy)
- knowledge:*     - Knowledge base (create, read, update, delete, publish)
- model:*         - Model management (create, read, update, delete)
- dataset:*       - Dataset management (create, read, update, delete)
- chat:*          - Chat functionality (create, read, delete)
- settings:*      - System settings (read, update)
- system:admin    - System administration
"""

# ==================== INTEGRATION CHECKLIST ====================
"""
□ 1. User Model Updated
   - Add role_id field to User model
   - Add role relationship
   - Default role: 'USER'

□ 2. Database Migration Created
   - Add role_id column to users table
   - Create Role table
   - Create Permission table
   - Create RolePermission mapping table

□ 3. Routes Protected
   - Auth routes: @require_permission(PermissionEnum.USER_READ/CREATE/UPDATE/DELETE)
   - Agent routes: @require_permission(PermissionEnum.AGENT_*)
   - Knowledge routes: @require_permission(PermissionEnum.KNOWLEDGE_*)
   - Chat routes: @require_permission(PermissionEnum.CHAT_*)
   - Admin routes: @require_role(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)

□ 4. API Endpoints Created
   - GET /api/v1/admin/roles - List all roles
   - GET /api/v1/admin/roles/{role_id} - Get role details
   - GET /api/v1/admin/permissions - List all permissions
   - GET /api/v1/admin/users/{user_id}/role - Get user's role
   - PUT /api/v1/admin/users/{user_id}/role - Assign role to user
   - GET /api/v1/admin/users/{user_id}/permissions - Get user's permissions
   - GET /api/v1/admin/statistics/roles - Role statistics

□ 5. Frontend Pages Created
   - /admin/roles-permissions - Role and permission management
   - /admin/users - User management with role assignment

□ 6. Testing Completed
   - Test permission checks with different roles
   - Test role assignment
   - Test permission inheritance
   - Test API endpoints
"""

# ==================== TESTING GUIDE ====================
"""
Test 1: Basic Permission Check
```bash
# Login as SUPER_ADMIN
curl -X POST http://localhost:8000/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email": "admin@admin.com", "password": "admin123"}'

# Try to list roles (should succeed)
curl -X GET http://localhost:8000/api/v1/admin/roles \\
  -H "Authorization: Bearer <token>"

# Login as USER and try the same (should fail with 403)
```

Test 2: Role Assignment
```bash
# Assign USER role to another user
curl -X PUT http://localhost:8000/api/v1/admin/users/{user_id}/role \\
  -H "Authorization: Bearer <admin_token>" \\
  -H "Content-Type: application/json" \\
  -d '{"role": "MANAGER"}'
```

Test 3: Permission Inheritance
```bash
# Get permissions for a user with EDITOR role
curl -X GET http://localhost:8000/api/v1/admin/users/{user_id}/permissions \\
  -H "Authorization: Bearer <admin_token>"

# Should return only the 8 permissions assigned to EDITOR role
```
"""

# ==================== PERMISSION MAPPING ====================
ROLE_PERMISSIONS_MAP = {
    "SUPER_ADMIN": [
        "user:create", "user:read", "user:update", "user:delete",
        "agent:create", "agent:read", "agent:update", "agent:delete", "agent:deploy",
        "knowledge:create", "knowledge:read", "knowledge:update", "knowledge:delete", "knowledge:publish",
        "model:create", "model:read", "model:update", "model:delete",
        "dataset:create", "dataset:read", "dataset:update", "dataset:delete",
        "chat:create", "chat:read", "chat:delete",
        "settings:read", "settings:update",
        "system:admin"
    ],
    "ADMIN": [
        "user:read", "user:update",
        "agent:create", "agent:read", "agent:update", "agent:delete",
        "knowledge:create", "knowledge:read", "knowledge:update", "knowledge:delete", "knowledge:publish",
        "model:read",
        "dataset:read",
        "chat:create", "chat:read", "chat:delete",
        "settings:read", "settings:update",
        "system:admin"
    ],
    "MANAGER": [
        "agent:create", "agent:read", "agent:update",
        "knowledge:create", "knowledge:read", "knowledge:update",
        "dataset:read",
        "chat:create", "chat:read", "chat:delete",
        "settings:read"
    ],
    "EDITOR": [
        "agent:read", "agent:update",
        "knowledge:create", "knowledge:read", "knowledge:update",
        "chat:create", "chat:read",
        "settings:read"
    ],
    "VIEWER": [
        "agent:read",
        "knowledge:read",
        "dataset:read",
        "settings:read"
    ],
    "USER": [
        "chat:create", "chat:read",
        "knowledge:read"
    ]
}
