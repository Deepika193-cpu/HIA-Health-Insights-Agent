import groq
import streamlit as st
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)

class ModelTier(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary" 
    TERTIARY = "tertiary"
    FALLBACK = "fallback"

class ModelManager:
    """
    Manages AI model selection, fallback, and rate limits.
    Implements an agent-based approach for model management.
    """
    
    MODEL_CONFIG = {
    ModelTier.PRIMARY: {
        "provider": "groq",
        "model": "openai/gpt-oss-120b",
        "max_tokens": 2000,
        "temperature": 0.7
    },
    ModelTier.SECONDARY: {
        "provider": "groq", 
        "model": "openai/gpt-oss-20b",
        "max_tokens": 2000,
        "temperature": 0.7
    },
    ModelTier.TERTIARY: {
        "provider": "groq",
        "model": "qwen/qwen3.6-27b",
        "max_tokens": 2000, 
        "temperature": 0.7
    },
    ModelTier.FALLBACK: {
        "provider": "groq",
        "model": "groq/compound-mini",
        "max_tokens": 2000,
        "temperature": 0.7
    }
}
    
    def __init__(self):
        self.clients = {}
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize API clients for each provider."""
        try:
            self.clients["groq"] = groq.Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")

    # Ordered cascade used for automatic fallback.
    TIER_ORDER = [
        ModelTier.PRIMARY,
        ModelTier.SECONDARY,
        ModelTier.TERTIARY,
        ModelTier.FALLBACK,
    ]

    def generate_analysis(self, data, system_prompt, retry_count=0, start_tier=None):
        """
        Generate analysis using the best available model with automatic fallback.
        Implements agent-based decision making for model selection.

        Args:
            start_tier: Optional ModelTier to start the cascade from (e.g. a user's
                "faster" or "more powerful" preference). Falls back down the
                remaining cascade on failure exactly like the default path.
        """
        if retry_count > 3:
            return {"success": False, "error": "All models failed after multiple retries"}

        # Determine which model tier to use based on retry count, honoring an
        # optional starting point in the cascade for the first attempt.
        base_order = self.TIER_ORDER
        if start_tier is not None and start_tier in base_order:
            start_index = base_order.index(start_tier)
            order = base_order[start_index:] + base_order[:start_index]
        else:
            order = base_order

        tier = order[min(retry_count, len(order) - 1)]

        model_config = self.MODEL_CONFIG[tier]
        provider = model_config["provider"]
        model = model_config["model"]
        
        # Check if we have a client for this provider
        if provider not in self.clients:
            logger.error(f"No client available for provider: {provider}")
            return self.generate_analysis(data, system_prompt, retry_count + 1, start_tier=start_tier)
            
        try:
            client = self.clients[provider]
            logger.info(f"Attempting generation with {provider} model: {model}")
            
            if provider == "groq":
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": str(data)}
                    ],
                    temperature=model_config["temperature"],
                    max_tokens=model_config["max_tokens"]
                )
                
                return {
                    "success": True,
                    "content": completion.choices[0].message.content,
                    "model_used": f"{provider}/{model}",
                    "tier_used": tier.value,
                }
                
        except Exception as e:
            error_message = str(e).lower()
            logger.warning(f"Model {model} failed: {error_message}")
            
            # Check for rate limit errors
            if "rate limit" in error_message or "quota" in error_message:
                # Wait briefly before retrying with a different model
                time.sleep(2)
            
            # Try next model in hierarchy
            return self.generate_analysis(data, system_prompt, retry_count + 1, start_tier=start_tier)
            
        return {"success": False, "error": "Analysis failed with all available models"}
