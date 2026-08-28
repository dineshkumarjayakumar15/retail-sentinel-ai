from fastapi import APIRouter
from app.config import settings
from app.schemas.settings import RiskSettingsSchema

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("", response_model=RiskSettingsSchema)
def get_settings():
    """Returns current risk thresholds and event scoring parameters."""
    return RiskSettingsSchema(
        SCORE_CUSTOMER_ENTERED=settings.SCORE_CUSTOMER_ENTERED,
        SCORE_SHELF_INTERACTION=settings.SCORE_SHELF_INTERACTION,
        SCORE_PRODUCT_PICKED=settings.SCORE_PRODUCT_PICKED,
        SCORE_PRODUCT_IN_BASKET=settings.SCORE_PRODUCT_IN_BASKET,
        SCORE_PRODUCT_RETURNED=settings.SCORE_PRODUCT_RETURNED,
        SCORE_PRODUCT_UNRESOLVED=settings.SCORE_PRODUCT_UNRESOLVED,
        SCORE_SUSPICIOUS_BEHAVIOR=settings.SCORE_SUSPICIOUS_BEHAVIOR,
        SCORE_POSSIBLE_CONCEALMENT=settings.SCORE_POSSIBLE_CONCEALMENT,
        SCORE_HIGH_RISK_DETECTED=settings.SCORE_HIGH_RISK_DETECTED,
        RISK_THRESHOLD_LOW=settings.RISK_THRESHOLD_LOW,
        RISK_THRESHOLD_MEDIUM=settings.RISK_THRESHOLD_MEDIUM,
        RISK_THRESHOLD_HIGH=settings.RISK_THRESHOLD_HIGH,
        RISK_THRESHOLD_CRITICAL=settings.RISK_THRESHOLD_CRITICAL,
    )

@router.put("", response_model=RiskSettingsSchema)
def update_settings(payload: RiskSettingsSchema):
    """Updates runtime risk thresholds and event weights."""
    settings.SCORE_CUSTOMER_ENTERED = payload.SCORE_CUSTOMER_ENTERED
    settings.SCORE_SHELF_INTERACTION = payload.SCORE_SHELF_INTERACTION
    settings.SCORE_PRODUCT_PICKED = payload.SCORE_PRODUCT_PICKED
    settings.SCORE_PRODUCT_IN_BASKET = payload.SCORE_PRODUCT_IN_BASKET
    settings.SCORE_PRODUCT_RETURNED = payload.SCORE_PRODUCT_RETURNED
    settings.SCORE_PRODUCT_UNRESOLVED = payload.SCORE_PRODUCT_UNRESOLVED
    settings.SCORE_SUSPICIOUS_BEHAVIOR = payload.SCORE_SUSPICIOUS_BEHAVIOR
    settings.SCORE_POSSIBLE_CONCEALMENT = payload.SCORE_POSSIBLE_CONCEALMENT
    settings.SCORE_HIGH_RISK_DETECTED = payload.SCORE_HIGH_RISK_DETECTED
    settings.RISK_THRESHOLD_LOW = payload.RISK_THRESHOLD_LOW
    settings.RISK_THRESHOLD_MEDIUM = payload.RISK_THRESHOLD_MEDIUM
    settings.RISK_THRESHOLD_HIGH = payload.RISK_THRESHOLD_HIGH
    settings.RISK_THRESHOLD_CRITICAL = payload.RISK_THRESHOLD_CRITICAL
    return get_settings()
