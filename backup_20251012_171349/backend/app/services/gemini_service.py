"""
Google Gemini AI service for HAZOP analysis suggestions.
"""
import os
import json
from typing import List, Dict, Optional
import google.generativeai as genai
from app.models.hazop import Node, Deviation

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 1.5 Flash for faster, cost-effective responses
MODEL_NAME = "gemini-1.5-flash"


class GeminiService:
    """Service for generating AI-powered HAZOP suggestions using Google Gemini."""

    def __init__(self):
        self.model = genai.GenerativeModel(MODEL_NAME)

    async def suggest_causes(
        self,
        node: Node,
        deviation_text: str,
        context: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """
        Generate AI suggestions for causes of a deviation.

        Args:
            node: HAZOP node information
            deviation_text: The deviation description
            context: Optional context (process description, P&ID info, etc.)

        Returns:
            List of cause suggestions with confidence scores
        """
        prompt = self._build_causes_prompt(node, deviation_text, context)

        try:
            response = await self._generate_response(prompt)
            suggestions = self._parse_suggestions(response)
            return suggestions
        except Exception as e:
            print(f"Error generating cause suggestions: {e}")
            return []

    async def suggest_consequences(
        self,
        node: Node,
        deviation_text: str,
        cause_text: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """
        Generate AI suggestions for consequences of a deviation.

        Args:
            node: HAZOP node information
            deviation_text: The deviation description
            cause_text: Optional cause description for more targeted suggestions
            context: Optional context

        Returns:
            List of consequence suggestions with confidence scores
        """
        prompt = self._build_consequences_prompt(node, deviation_text, cause_text, context)

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
        deviation_text: str,
        cause_text: Optional[str] = None,
        consequence_text: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """
        Generate AI suggestions for safeguards.

        Args:
            node: HAZOP node information
            deviation_text: The deviation description
            cause_text: Optional cause description
            consequence_text: Optional consequence description
            context: Optional context

        Returns:
            List of safeguard suggestions with confidence scores
        """
        prompt = self._build_safeguards_prompt(
            node, deviation_text, cause_text, consequence_text, context
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
        deviation_text: str,
        context: Optional[Dict]
    ) -> str:
        """Build prompt for cause suggestions."""
        prompt = f"""You are an expert HAZOP (Hazard and Operability Study) analyst with deep knowledge of process safety.

HAZOP Node Information:
- Equipment/Component: {node.node_number}
- Parameter: {node.parameter or 'Not specified'}
- Guide Word: {node.guide_word or 'Not specified'}
- Deviation: {deviation_text}

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
        deviation_text: str,
        cause_text: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """Build prompt for consequence suggestions."""
        cause_info = f"\n- Known Cause: {cause_text}" if cause_text else ""

        prompt = f"""You are an expert HAZOP analyst specializing in consequence analysis and risk assessment.

HAZOP Node Information:
- Equipment/Component: {node.node_number}
- Parameter: {node.parameter or 'Not specified'}
- Guide Word: {node.guide_word or 'Not specified'}
- Deviation: {deviation_text}{cause_info}

Task: Suggest 3-5 realistic CONSEQUENCES of this deviation. Each consequence should:
1. Be specific about the impact (safety, environmental, operational, economic)
2. Consider severity and likelihood
3. Follow logical cause-effect relationships
4. Include both immediate and potential cascading effects

{self._add_context_to_prompt(context)}

Return your response as a JSON array with this exact format:
[
  {{"text": "Consequence description", "confidence": 80, "severity": "High", "category": "Safety"}},
  {{"text": "Another consequence", "confidence": 70, "severity": "Medium", "category": "Operational"}}
]

Severity levels: Critical, High, Medium, Low
Categories: Safety, Environmental, Operational, Economic

Confidence score (0-100):
- 90-100: Highly likely consequence based on physics/chemistry
- 70-89: Probable consequence depending on conditions
- 50-69: Possible consequence requiring specific scenarios
- Below 50: Less likely but potential worst-case

Only return the JSON array, no other text."""

        return prompt

    def _build_safeguards_prompt(
        self,
        node: Node,
        deviation_text: str,
        cause_text: Optional[str],
        consequence_text: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """Build prompt for safeguard suggestions."""
        cause_info = f"\n- Known Cause: {cause_text}" if cause_text else ""
        consequence_info = f"\n- Known Consequence: {consequence_text}" if consequence_text else ""

        prompt = f"""You are an expert HAZOP analyst specializing in process safety safeguards and risk mitigation.

HAZOP Node Information:
- Equipment/Component: {node.node_number}
- Parameter: {node.parameter or 'Not specified'}
- Guide Word: {node.guide_word or 'Not specified'}
- Deviation: {deviation_text}{cause_info}{consequence_info}

Task: Suggest 3-5 SAFEGUARDS to prevent, detect, or mitigate this deviation. Each safeguard should:
1. Be specific and implementable
2. Follow the hierarchy of controls (elimination > substitution > engineering > administrative > PPE)
3. Be appropriate for the risk level
4. Consider both existing and recommended safeguards

{self._add_context_to_prompt(context)}

Return your response as a JSON array with this exact format:
[
  {{"text": "Safeguard description", "confidence": 85, "type": "Engineering", "effectiveness": "High"}},
  {{"text": "Another safeguard", "confidence": 75, "type": "Administrative", "effectiveness": "Medium"}}
]

Safeguard types: Engineering, Administrative, Detection, Procedural, PPE
Effectiveness: High, Medium, Low

Confidence score (0-100):
- 90-100: Industry standard safeguard, proven effective
- 70-89: Recommended safeguard, effective in most scenarios
- 50-69: Useful safeguard, effectiveness depends on implementation
- Below 50: Additional safeguard, may help in specific cases

Only return the JSON array, no other text."""

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
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,  # Lower temperature for more focused, consistent responses
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
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
