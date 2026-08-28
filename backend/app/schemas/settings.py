from pydantic import BaseModel, ConfigDict

class RiskSettingsSchema(BaseModel):
    SCORE_CUSTOMER_ENTERED: float
    SCORE_SHELF_INTERACTION: float
    SCORE_PRODUCT_PICKED: float
    SCORE_PRODUCT_IN_BASKET: float
    SCORE_PRODUCT_RETURNED: float
    SCORE_PRODUCT_UNRESOLVED: float
    SCORE_SUSPICIOUS_BEHAVIOR: float
    SCORE_POSSIBLE_CONCEALMENT: float
    SCORE_HIGH_RISK_DETECTED: float

    RISK_THRESHOLD_LOW: float
    RISK_THRESHOLD_MEDIUM: float
    RISK_THRESHOLD_HIGH: float
    RISK_THRESHOLD_CRITICAL: float

    model_config = ConfigDict(from_attributes=True)
