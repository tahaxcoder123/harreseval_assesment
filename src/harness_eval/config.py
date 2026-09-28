"""Configuration and evaluation policy settings."""
from typing import Dict, Any
from pydantic import BaseModel, Field


class DecisionPolicy(BaseModel):
    """Configurable decision policy governing POSITIVE, NEGATIVE, or INCONCLUSIVE verdicts."""
    
    # Minimum correctness rate improvement needed for positive verdict (+10 percentage points)
    min_correctness_delta: float = 0.08
    
    # Maximum tolerable task regressions before requiring INCONCLUSIVE or NEGATIVE
    max_tolerated_regressions: int = 0
    
    # Maximum acceptable percentage cost increase before flagging trade-off
    max_cost_increase_pct: float = 60.0
    
    # Minimum tasks or sample size required to avoid small-sample uncertainty
    min_sample_size_for_certainty: int = 10
    
    # Minimum requirement satisfaction rate improvement
    min_requirement_delta: float = 0.05
    
    # Minimum convention compliance rate
    min_candidate_compliance_rate: float = 0.80


DEFAULT_POLICY = DecisionPolicy()
