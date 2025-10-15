"""
Google Gemini AI service for HAZOP analysis suggestions.
"""
import os
import json
from typing import List, Dict, Optional
import google.generativeai as genai
from app.models.study import HazopNode as Node, Deviation

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 2.5 Flash for faster, cost-effective responses
# This is the latest stable flash model as of October 2025
MODEL_NAME = "gemini-2.5-flash"


class GeminiService:
    """Service for generating AI-powered HAZOP suggestions using Google Gemini."""

    def __init__(self):
        self.api_key_configured = bool(GEMINI_API_KEY)
        if self.api_key_configured:
            self.model = genai.GenerativeModel(MODEL_NAME)
        else:
            self.model = None
            print("[Gemini] WARNING: GEMINI_API_KEY not configured. AI suggestions will not be available.")

    async def suggest_causes(
        self,
        node: Node,
        deviation: "Deviation",
        context: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """
        Generate AI suggestions for causes of a deviation.

        Args:
            node: HAZOP node information
            deviation: The deviation object with parameter, guide_word, and description
            context: Optional context (process description, P&ID info, etc.)

        Returns:
            List of cause suggestions with confidence scores
        """
        if not self.api_key_configured:
            print("[Gemini] API key not configured, returning empty suggestions")
            return []

        prompt = self._build_causes_prompt(node, deviation, context)

        print(f"[Gemini] Generating cause suggestions for deviation: {deviation.parameter}/{deviation.guide_word}")
        print(f"[Gemini] Context provided: {context}")

        try:
            response = await self._generate_response(prompt)
            print(f"[Gemini] Raw response received: {response[:200]}...")
            suggestions = self._parse_suggestions(response)
            print(f"[Gemini] Parsed {len(suggestions)} suggestions")
            return suggestions
        except Exception as e:
            print(f"[Gemini] Error generating cause suggestions: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def suggest_consequences(
        self,
        node: Node,
        deviation: "Deviation",
        cause_text: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """
        Generate AI suggestions for consequences of a deviation.

        Args:
            node: HAZOP node information
            deviation: The deviation object
            cause_text: Optional cause description for more targeted suggestions
            context: Optional context

        Returns:
            List of consequence suggestions with confidence scores
        """
        if not self.api_key_configured:
            print("[Gemini] API key not configured, returning empty suggestions")
            return []

        prompt = self._build_consequences_prompt(node, deviation, cause_text, context)

        try:
            response = await self._generate_response(prompt)
            suggestions = self._parse_suggestions(response)
            return suggestions
        except Exception as e:
            print(f"Error generating consequence suggestions: {e}")
            return []

    async def suggest_safeguards(
        self,
        node: Node,
        deviation: "Deviation",
        cause_text: Optional[str] = None,
        consequence_text: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """
        Generate AI suggestions for safeguards.

        Args:
            node: HAZOP node information
            deviation: The deviation object
            cause_text: Optional cause description
            consequence_text: Optional consequence description
            context: Optional context

        Returns:
            List of safeguard suggestions with confidence scores
        """
        if not self.api_key_configured:
            print("[Gemini] API key not configured, returning empty suggestions")
            return []

        prompt = self._build_safeguards_prompt(
            node, deviation, cause_text, consequence_text, context
        )

        try:
            response = await self._generate_response(prompt)
            suggestions = self._parse_suggestions(response)
            return suggestions
        except Exception as e:
            print(f"Error generating safeguard suggestions: {e}")
            return []

    async def suggest_complete_analysis(
        self,
        node: Node,
        deviation_text: str,
        context: Optional[Dict] = None
    ) -> Dict[str, List[Dict[str, any]]]:
        """
        Generate complete analysis: causes, consequences, and safeguards in one call.

        Args:
            node: HAZOP node information
            deviation_text: The deviation description
            context: Optional context

        Returns:
            Dictionary with 'causes', 'consequences', and 'safeguards' lists
        """
        if not self.api_key_configured:
            print("[Gemini] API key not configured, returning empty analysis")
            return {"causes": [], "consequences": [], "safeguards": []}

        prompt = self._build_complete_analysis_prompt(node, deviation_text, context)

        try:
            response = await self._generate_response(prompt)
            analysis = self._parse_complete_analysis(response)
            return analysis
        except Exception as e:
            print(f"Error generating complete analysis: {e}")
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
                "temperature": 0.4,  # Slightly higher for more natural technical responses
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 4096,  # Increased for complete responses
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


# Singleton instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create Gemini service singleton."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
