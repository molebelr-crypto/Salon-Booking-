"""
Permission and access control
"""
from typing import Optional
from models import TenantModel, SubscriptionPlanEnum
from config import config
from utils.logger import get_logger

logger = get_logger("permissions")


class PermissionManager:
    """Manage permissions and feature access"""
    
    # Feature limits per subscription plan
    PLAN_LIMITS = {
        SubscriptionPlanEnum.TRIAL: {
            "max_staff": 1,
            "max_bookings": config.TRIAL_BOOKINGS_LIMIT,
            "features": ["basic_booking", "customer_management"]
        },
        SubscriptionPlanEnum.BASIC: {
            "max_staff": 1,
            "max_bookings": 100,
            "features": [
                "basic_booking",
                "customer_management",
                "service_management",
                "staff_management",
                "basic_analytics"
            ]
        },
        SubscriptionPlanEnum.STANDARD: {
            "max_staff": 5,
            "max_bookings": 500,
            "features": [
                "basic_booking",
                "customer_management",
                "service_management",
                "staff_management",
                "reminders",
                "analytics",
                "loyalty_system",
                "promo_codes",
                "waiting_list"
            ]
        },
        SubscriptionPlanEnum.PREMIUM: {
            "max_staff": float('inf'),
            "max_bookings": float('inf'),
            "features": [
                "all",  # All features
                "branches",
                "advanced_analytics",
                "custom_reports",
                "api_access",
                "white_label"
            ]
        },
        SubscriptionPlanEnum.LIFETIME: {
            "max_staff": float('inf'),
            "max_bookings": float('inf'),
            "features": ["all"]
        }
    }
    
    @staticmethod
    def has_feature(tenant: TenantModel, feature: str) -> bool:
        """Check if tenant has access to a feature"""
        if not tenant or not tenant.is_active or tenant.is_banned:
            return False
        
        # Get features for this plan
        plan = tenant.subscription_plan
        if plan not in PermissionManager.PLAN_LIMITS:
            return False
        
        features = PermissionManager.PLAN_LIMITS[plan]["features"]
        
        # "all" means all features available
        if "all" in features:
            return True
        
        return feature in features
    
    @staticmethod
    def can_add_staff(tenant: TenantModel, current_staff_count: int) -> bool:
        """Check if tenant can add more staff"""
        if not tenant or not tenant.is_active:
            return False
        
        plan = tenant.subscription_plan
        if plan not in PermissionManager.PLAN_LIMITS:
            return False
        
        max_staff = PermissionManager.PLAN_LIMITS[plan]["max_staff"]
        return current_staff_count < max_staff
    
    @staticmethod
    def can_add_booking(tenant: TenantModel, current_booking_count: int) -> bool:
        """Check if tenant can add more bookings"""
        if not tenant or not tenant.is_active:
            return False
        
        plan = tenant.subscription_plan
        if plan not in PermissionManager.PLAN_LIMITS:
            return False
        
        max_bookings = PermissionManager.PLAN_LIMITS[plan]["max_bookings"]
        return current_booking_count < max_bookings
    
    @staticmethod
    def check_premium_feature(tenant: TenantModel, feature: str) -> bool:
        """Check if feature is available and log access"""
        has_access = PermissionManager.has_feature(tenant, feature)
        
        if not has_access:
            logger.warning(
                f"Tenant {tenant.tenant_id} attempted to access "
                f"restricted feature: {feature} (Plan: {tenant.subscription_plan})"
            )
        
        return has_access
    
    @staticmethod
    def get_available_features(tenant: TenantModel) -> list:
        """Get list of available features for tenant"""
        if not tenant:
            return []
        
        plan = tenant.subscription_plan
        if plan not in PermissionManager.PLAN_LIMITS:
            return []
        
        features = PermissionManager.PLAN_LIMITS[plan]["features"]
        
        if "all" in features:
            # Return all possible features
            all_features = set()
            for plan_features in PermissionManager.PLAN_LIMITS.values():
                all_features.update(plan_features["features"])
            all_features.discard("all")
            return list(all_features)
        
        return features
    
    @staticmethod
    def get_plan_limits(plan: str) -> dict:
        """Get limits for a subscription plan"""
        return PermissionManager.PLAN_LIMITS.get(plan, {})


# Subscription plan descriptions for user interface
PLAN_DESCRIPTIONS = {
    SubscriptionPlanEnum.TRIAL: {
        "name": "Trial",
        "price": "FREE",
        "duration": f"{config.TRIAL_DAYS} days",
        "description": f"Try for free for {config.TRIAL_DAYS} days"
    },
    SubscriptionPlanEnum.BASIC: {
        "name": "Basic",
        "price": "$9.99/month",
        "description": "Perfect for solo barbers"
    },
    SubscriptionPlanEnum.STANDARD: {
        "name": "Standard",
        "price": "$19.99/month",
        "description": "For growing salons"
    },
    SubscriptionPlanEnum.PREMIUM: {
        "name": "Premium",
        "price": "$49.99/month",
        "description": "For established salons with multiple branches"
    },
    SubscriptionPlanEnum.LIFETIME: {
        "name": "Lifetime",
        "price": "$999 one-time",
        "description": "Unlimited everything, forever"
    }
}
