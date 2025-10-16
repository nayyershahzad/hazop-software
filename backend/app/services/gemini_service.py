"""
Google Gemini AI service for HAZOP analysis suggestions.
Includes caching system to reduce API costs by approximately 70%.
"""
import os
import json
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import google.generativeai as genai
from app.models.study import HazopNode as Node, Deviation
from app.services.gemini_cache import GeminiCacheService

# Configure logger
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not configured. AI suggestions will not be available.")

# Use Gemini 2.5 Flash for faster, cost-effective responses
# This is the latest stable flash model as of October 2025
MODEL_NAME = "gemini-2.5-flash"

# Enable caching by default
ENABLE_CACHING = os.getenv("ENABLE_GEMINI_CACHE", "true").lower() in ("true", "1", "yes")


class GeminiService:
    """Service for generating AI-powered HAZOP suggestions using Google Gemini."""

    def __init__(self):
        self.api_key_configured = bool(GEMINI_API_KEY)
        self.caching_enabled = ENABLE_CACHING

        if self.api_key_configured:
            self.model = genai.GenerativeModel(MODEL_NAME)
            logger.info(f"Gemini service initialized with model: {MODEL_NAME}")
            logger.info(f"Caching system is {'enabled' if self.caching_enabled else 'disabled'}")
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not configured. AI suggestions will not be available.")

    async def suggest_causes(
        self,
        node: Node,
        deviation: "Deviation",
        context: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> List[Dict[str, any]]:
        """
        Generate AI suggestions for causes of a deviation.

        Uses caching to reduce API costs by ~70%.

        Args:
            node: HAZOP node information
            deviation: The deviation object with parameter, guide_word, and description
            context: Optional context (process description, P&ID info, etc.)
            db: Database session (required for caching)

        Returns:
            List of cause suggestions with confidence scores
        """
        if not self.api_key_configured:
            logger.warning("API key not configured, returning empty suggestions")
            return []

        # Setup cache service if DB session provided and caching enabled
        cache_service = None
        if self.caching_enabled and db is not None:
            cache_service = GeminiCacheService(db)

        # Try to get from cache first
        context_dict = context or {}
        if cache_service:
            cached_response = cache_service.get_cached_response(
                deviation_id=str(deviation.id),
                context=context_dict,
                suggestion_type='causes'
            )

            if cached_response:
                # Add indicator that these are cached results (can be removed for production)
                for suggestion in cached_response:
                    suggestion['cached'] = True

                logger.info(f"Cache hit for causes (deviation: {deviation.id})")
                return cached_response

        # Cache miss - proceed with API call
        prompt = self._build_causes_prompt(node, deviation, context)

        logger.info(f"Generating cause suggestions for deviation: {deviation.parameter}/{deviation.guide_word}")
        logger.debug(f"Context provided: {context}")

        try:
            response = await self._generate_response(prompt)
            logger.debug(f"Raw response received: {response[:100]}...")
            suggestions = self._parse_suggestions(response)
            logger.info(f"Parsed {len(suggestions)} cause suggestions")

            # Cache the successful response if caching enabled
            if cache_service and suggestions:
                cache_service.cache_response(
                    deviation_id=str(deviation.id),
                    context=context_dict,
                    suggestion_type='causes',
                    response=suggestions
                )

            return suggestions
        except Exception as e:
            logger.error(f"Error generating cause suggestions: {e}", exc_info=True)
            return []

    async def suggest_consequences(
        self,
        node: Node,
        deviation: "Deviation",
        cause_text: Optional[str] = None,
        context: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> List[Dict[str, any]]:
        """
        Generate AI suggestions for consequences of a deviation.

        Uses caching to reduce API costs by ~70%.

        Args:
            node: HAZOP node information
            deviation: The deviation object
            cause_text: Optional cause description for more targeted suggestions
            context: Optional context
            db: Database session (required for caching)

        Returns:
            List of consequence suggestions with confidence scores
        """
        if not self.api_key_configured:
            logger.warning("API key not configured, returning empty suggestions")
            return []

        # Setup cache service if DB session provided and caching enabled
        cache_service = None
        if self.caching_enabled and db is not None:
            cache_service = GeminiCacheService(db)

        # Enhanced cache key that includes the cause_text
        context_dict = context or {}
        if cause_text:
            # Include cause text in context for cache key generation
            context_dict = dict(context_dict)
            context_dict["cause_text"] = cause_text

        # Try to get from cache first
        if cache_service:
            cached_response = cache_service.get_cached_response(
                deviation_id=str(deviation.id),
                context=context_dict,
                suggestion_type='consequences'
            )

            if cached_response:
                # Add indicator that these are cached results
                for suggestion in cached_response:
                    suggestion['cached'] = True

                logger.info(f"Cache hit for consequences (deviation: {deviation.id})")
                return cached_response

        # Cache miss - proceed with API call
        prompt = self._build_consequences_prompt(node, deviation, cause_text, context)

        logger.info(f"Generating consequence suggestions for deviation: {deviation.parameter}/{deviation.guide_word}")

        try:
            response = await self._generate_response(prompt)
            suggestions = self._parse_suggestions(response)
            logger.info(f"Parsed {len(suggestions)} consequence suggestions")

            # Cache the successful response if caching enabled
            if cache_service and suggestions:
                cache_service.cache_response(
                    deviation_id=str(deviation.id),
                    context=context_dict,
                    suggestion_type='consequences',
                    response=suggestions
                )

            return suggestions
        except Exception as e:
            logger.error(f"Error generating consequence suggestions: {e}", exc_info=True)
            return []

    async def suggest_safeguards(
        self,
        node: Node,
        deviation: "Deviation",
        cause_text: Optional[str] = None,
        consequence_text: Optional[str] = None,
        context: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> List[Dict[str, any]]:
        """
        Generate AI suggestions for safeguards.

        Uses caching to reduce API costs by ~70%.

        Args:
            node: HAZOP node information
            deviation: The deviation object
            cause_text: Optional cause description
            consequence_text: Optional consequence description
            context: Optional context
            db: Database session (required for caching)

        Returns:
            List of safeguard suggestions with confidence scores
        """
        if not self.api_key_configured:
            logger.warning("API key not configured, returning empty suggestions")
            return []

        # Setup cache service if DB session provided and caching enabled
        cache_service = None
        if self.caching_enabled and db is not None:
            cache_service = GeminiCacheService(db)

        # Enhanced cache key that includes cause and consequence text
        context_dict = context or {}
        if cause_text or consequence_text:
            # Include related text in context for cache key generation
            context_dict = dict(context_dict)
            if cause_text:
                context_dict["cause_text"] = cause_text
            if consequence_text:
                context_dict["consequence_text"] = consequence_text

        # Try to get from cache first
        if cache_service:
            cached_response = cache_service.get_cached_response(
                deviation_id=str(deviation.id),
                context=context_dict,
                suggestion_type='safeguards'
            )

            if cached_response:
                # Add indicator that these are cached results
                for suggestion in cached_response:
                    suggestion['cached'] = True

                logger.info(f"Cache hit for safeguards (deviation: {deviation.id})")
                return cached_response

        # Cache miss - proceed with API call
        prompt = self._build_safeguards_prompt(
            node, deviation, cause_text, consequence_text, context
        )

        logger.info(f"Generating safeguard suggestions for deviation: {deviation.parameter}/{deviation.guide_word}")

        try:
            response = await self._generate_response(prompt)
            suggestions = self._parse_suggestions(response)
            logger.info(f"Parsed {len(suggestions)} safeguard suggestions")

            # Cache the successful response if caching enabled
            if cache_service and suggestions:
                cache_service.cache_response(
                    deviation_id=str(deviation.id),
                    context=context_dict,
                    suggestion_type='safeguards',
                    response=suggestions
                )

            return suggestions
        except Exception as e:
            logger.error(f"Error generating safeguard suggestions: {e}", exc_info=True)
            return []

    async def suggest_complete_analysis(
        self,
        node: Node,
        deviation_text: str,
        context: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> Dict[str, List[Dict[str, any]]]:
        """
        Generate complete analysis: causes, consequences, and safeguards in one call.

        Uses caching to reduce API costs by ~70%.

        Args:
            node: HAZOP node information
            deviation_text: The deviation description
            context: Optional context
            db: Database session (required for caching)

        Returns:
            Dictionary with 'causes', 'consequences', and 'safeguards' lists
        """
        if not self.api_key_configured:
            logger.warning("API key not configured, returning empty analysis")
            return {"causes": [], "consequences": [], "safeguards": []}

        # Setup cache service if DB session provided and caching enabled
        cache_service = None
        if self.caching_enabled and db is not None:
            cache_service = GeminiCacheService(db)

        # Enhanced cache key for complete analysis
        context_dict = context or {}
        if deviation_text:
            context_dict = dict(context_dict)
            context_dict["deviation_text"] = deviation_text

        # Try to get from cache first
        if cache_service:
            cached_response = cache_service.get_cached_response(
                # Use node ID since we don't have a deviation ID in this case
                deviation_id=str(node.id),
                context=context_dict,
                suggestion_type='complete_analysis'
            )

            if cached_response:
                # Add indicator that these are cached results
                for section in ['causes', 'consequences', 'safeguards']:
                    for item in cached_response.get(section, []):
                        item['cached'] = True

                logger.info(f"Cache hit for complete analysis (node: {node.id})")
                return cached_response

        # Cache miss - proceed with API call
        prompt = self._build_complete_analysis_prompt(node, deviation_text, context)

        logger.info(f"Generating complete analysis for node: {node.node_name}")

        try:
            response = await self._generate_response(prompt)
            analysis = self._parse_complete_analysis(response)

            logger.info(f"Parsed complete analysis: {len(analysis.get('causes', []))} causes, " +
                      f"{len(analysis.get('consequences', []))} consequences, " +
                      f"{len(analysis.get('safeguards', []))} safeguards")

            # Cache the successful response if caching enabled
            if cache_service and any(len(analysis.get(k, [])) > 0 for k in ['causes', 'consequences', 'safeguards']):
                cache_service.cache_response(
                    deviation_id=str(node.id),
                    context=context_dict,
                    suggestion_type='complete_analysis',
                    response=analysis
                )

            return analysis
        except Exception as e:
            logger.error(f"Error generating complete analysis: {e}", exc_info=True)
            return {"causes": [], "consequences": [], "safeguards": []}

    def _build_causes_prompt(
        self,
        node: Node,
        deviation: "Deviation",
        context: Optional[Dict]
    ) -> str:
        """Build prompt for cause suggestions."""
        prompt = f"""You are an expert HAZOP (Hazard and Operability Study) analyst with deep knowledge of process safety.

HAZOP Node Information:
- Equipment/Component: {node.node_number} - {node.node_name}
- Parameter: {deviation.parameter}
- Guide Word: {deviation.guide_word}
- Deviation: {deviation.deviation_description}

Task: Suggest 3-5 realistic CAUSES for this deviation. Each cause should be:
1. Specific and actionable
2. Technically accurate for process safety
3. Relevant to the equipment and parameter
4. Based on common failure modes in industrial processes

{self._add_context_to_prompt(context)}

Return your response as a JSON array with this exact format:
[
  {{"text": "Cause description", "confidence": 85, "reasoning": "Brief explanation"}},
  {{"text": "Another cause", "confidence": 75, "reasoning": "Brief explanation"}}
]

Confidence score (0-100):
- 90-100: Very common cause, well-documented in literature
- 70-89: Likely cause based on equipment type and parameter
- 50-69: Possible cause, depends on specific conditions
- Below 50: Less likely but worth considering

Only return the JSON array, no other text."""

        return prompt

    def _build_consequences_prompt(
        self,
        node: Node,
        deviation: "Deviation",
        cause_text: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """Build prompt for consequence suggestions."""
        cause_info = f"\n- Known Cause: {cause_text}" if cause_text else ""

        prompt = f"""You are a HAZOP analyst performing consequence analysis.

Equipment: {node.node_number} - {node.node_name}
Parameter: {deviation.parameter}
Guide Word: {deviation.guide_word}
Deviation: {deviation.deviation_description}{cause_info}

{self._add_context_to_prompt(context)}

Task: List 3-5 potential consequences (safety, environmental, operational, or economic impacts).

Return JSON array in this format:
[
  {{"text": "Impact on process operations", "confidence": 80, "severity": "Medium", "category": "Operational"}},
  {{"text": "Equipment stress or strain", "confidence": 70, "severity": "Low", "category": "Economic"}}
]

Only return valid JSON, no other text."""

        return prompt

    def _build_safeguards_prompt(
        self,
        node: Node,
        deviation: "Deviation",
        cause_text: Optional[str],
        consequence_text: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """Build prompt for safeguard suggestions."""
        cause_info = f"\n- Known Cause: {cause_text}" if cause_text else ""
        consequence_info = f"\n- Known Consequence: {consequence_text}" if consequence_text else ""

        prompt = f"""You are a HAZOP analyst suggesting process safety controls.

Equipment: {node.node_number} - {node.node_name}
Parameter: {deviation.parameter}
Guide Word: {deviation.guide_word}
Deviation: {deviation.deviation_description}{cause_info}{consequence_info}

{self._add_context_to_prompt(context)}

Task: List 3-5 safeguards or controls to prevent, detect, or reduce this deviation.

Return JSON array format:
[
  {{"text": "Control measure description", "confidence": 85, "type": "Engineering", "effectiveness": "High"}},
  {{"text": "Monitoring or detection method", "confidence": 75, "type": "Detection", "effectiveness": "Medium"}}
]

Types: Engineering, Administrative, Detection, Procedural
Effectiveness: High, Medium, Low

Only return valid JSON, no other text."""

        return prompt

    def _build_complete_analysis_prompt(
        self,
        node: Node,
        deviation_text: str,
        context: Optional[Dict]
    ) -> str:
        """Build prompt for complete analysis."""
        prompt = f"""You are an expert HAZOP analyst performing a complete hazard and operability analysis.

HAZOP Node Information:
- Equipment/Component: {node.node_number}
- Parameter: {node.parameter or 'Not specified'}
- Guide Word: {node.guide_word or 'Not specified'}
- Deviation: {deviation_text}

Task: Provide a complete HAZOP analysis with causes, consequences, and safeguards.

{self._add_context_to_prompt(context)}

Return your response as a JSON object with this exact format:
{{
  "causes": [
    {{"text": "Cause description", "confidence": 85, "reasoning": "Brief explanation"}}
  ],
  "consequences": [
    {{"text": "Consequence description", "confidence": 80, "severity": "High", "category": "Safety"}}
  ],
  "safeguards": [
    {{"text": "Safeguard description", "confidence": 85, "type": "Engineering", "effectiveness": "High"}}
  ]
}}

Guidelines:
- Provide 3-5 items for each category
- Focus on realistic, industry-standard scenarios
- Use appropriate confidence scores (0-100)
- Consider the hierarchy of controls for safeguards
- Include both immediate and cascading consequences

Only return the JSON object, no other text."""

        return prompt

    def _add_context_to_prompt(self, context: Optional[Dict]) -> str:
        """Add optional context information to prompt."""
        if not context:
            return ""

        context_text = "\nAdditional Context:"

        if context.get("process_description"):
            context_text += f"\n- Process: {context['process_description']}"

        if context.get("fluid_type"):
            context_text += f"\n- Fluid: {context['fluid_type']}"

        if context.get("operating_conditions"):
            context_text += f"\n- Operating Conditions: {context['operating_conditions']}"

        if context.get("previous_incidents"):
            context_text += f"\n- Previous Incidents: {context['previous_incidents']}"

        return context_text

    async def _generate_response(self, prompt: str) -> str:
        """Generate response from Gemini API."""
        try:
            # Configure safety settings to be less restrictive for technical content
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            generation_config = {
                "temperature": 0.3,  # Lower for faster, more consistent responses
                "top_p": 0.8,
                "top_k": 20,  # Reduced for faster token selection
                "max_output_tokens": 2048,  # Reduced for faster response
            }

            # Run the blocking Gemini API call in a thread pool executor
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: self.model.generate_content(
                        prompt,
                        generation_config=generation_config,
                        safety_settings=safety_settings
                    )
                )

            # Check if response was blocked
            if not response.candidates or not response.candidates[0].content.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                print(f"Gemini API blocked response. Finish reason: {finish_reason}")
                print(f"Safety ratings: {response.candidates[0].safety_ratings if response.candidates else 'N/A'}")
                return "[]"  # Return empty array for parsing

            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise

    def _parse_suggestions(self, response: str) -> List[Dict[str, any]]:
        """Parse JSON response into list of suggestions."""
        try:
            # Try to extract JSON from response
            response = response.strip()

            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            response = response.strip()

            suggestions = json.loads(response)

            # Ensure it's a list
            if not isinstance(suggestions, list):
                return []

            return suggestions
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response was: {response}")
            return []

    def _parse_complete_analysis(self, response: str) -> Dict[str, List[Dict[str, any]]]:
        """Parse JSON response for complete analysis."""
        try:
            # Try to extract JSON from response
            response = response.strip()

            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            response = response.strip()

            analysis = json.loads(response)

            # Ensure all required keys exist
            if not isinstance(analysis, dict):
                return {"causes": [], "consequences": [], "safeguards": []}

            return {
                "causes": analysis.get("causes", []),
                "consequences": analysis.get("consequences", []),
                "safeguards": analysis.get("safeguards", [])
            }
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response was: {response}")
            return {"causes": [], "consequences": [], "safeguards": []}


# Cache cleanup background task
async def cleanup_expired_cache(db: Session):
    """Cleanup expired cache entries periodically"""
    try:
        cache_service = GeminiCacheService(db)
        deleted_count = cache_service.cleanup_expired()
        logger.info(f"Cache cleanup completed: {deleted_count} expired entries removed")
    except Exception as e:
        logger.error(f"Error during cache cleanup: {e}", exc_info=True)

# Singleton instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create Gemini service singleton."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service

# Schedule periodic cache cleanup (every 24 hours)
def schedule_cache_cleanup(db_factory):
    """
    Schedule periodic cache cleanup to remove expired entries.

    This should be called at application startup with a
    factory function that creates database sessions.
    """
    import asyncio
    from datetime import datetime, timedelta

    async def _cleanup_task():
        while True:
            try:
                # Get a new DB session
                db = next(db_factory())

                # Run cleanup
                logger.info("Running scheduled Gemini cache cleanup...")
                await cleanup_expired_cache(db)

                # Sleep for 24 hours
                await asyncio.sleep(24 * 60 * 60)
            except Exception as e:
                logger.error(f"Error in cache cleanup task: {e}", exc_info=True)
                # Sleep for 1 hour before retry
                await asyncio.sleep(60 * 60)

    # Start the task
    asyncio.create_task(_cleanup_task())
    logger.info("Gemini cache cleanup scheduled to run every 24 hours")
