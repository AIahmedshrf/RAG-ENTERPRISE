"""
Multi-tenancy Middleware
"""
from fastapi import Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional

from api.database import get_db
from api.models import Tenant, User
from api.middleware.auth import get_current_user
from utilities.logger import get_logger

logger = get_logger(__name__)


class TenantMiddleware:
    """Multi-tenancy middleware"""
    
    @staticmethod
    def get_tenant_from_request(request: Request, db: Session) -> Optional[Tenant]:
        """Extract tenant from request"""
        # Method 1: Header
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            tenant = db.query(Tenant).filter(
                Tenant.id == tenant_id,
                Tenant.is_active == True
            ).first()
            if tenant:
                return tenant
        
        # Method 2: Subdomain
        host = request.headers.get('Host', '')
        parts = host.split('.')
        if len(parts) > 2:
            slug = parts[0]
            tenant = db.query(Tenant).filter(
                Tenant.slug == slug,
                Tenant.is_active == True
            ).first()
            if tenant:
                return tenant
        
        # Method 3: Path parameter
        path_parts = request.url.path.split('/')
        if len(path_parts) > 3 and path_parts[2] == 'tenants':
            tenant_id = path_parts[3]
            tenant = db.query(Tenant).filter(
                Tenant.id == tenant_id,
                Tenant.is_active == True
            ).first()
            if tenant:
                return tenant
        
        return None


async def get_current_tenant(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Tenant:
    """Get current tenant from request or user"""
    tenant = TenantMiddleware.get_tenant_from_request(request, db)
    
    if tenant:
        if current_user.tenant_id != tenant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )
        return tenant
    
    tenant = db.query(Tenant).filter(
        Tenant.id == current_user.tenant_id,
        Tenant.is_active == True
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or inactive"
        )
    
    return tenant
