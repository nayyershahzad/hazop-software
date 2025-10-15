# Gemini AI Integration for HAZOP Software

This document describes the integration of Google's Gemini AI capabilities into the HAZOP Software to enhance process safety analysis.

## Overview

The Gemini integration adds powerful AI capabilities to the HAZOP analysis process, including:

1. **AI-powered Insights**: Generate suggestions for causes, consequences, safeguards, and recommendations based on process context.
2. **Smart Risk Assessment**: Receive data-informed suggestions for risk level evaluation.
3. **Safeguard Effectiveness Evaluation**: Analyze safeguard effectiveness and get improvement suggestions.
4. **Contextual Knowledge Injection**: Access relevant regulations, industry incidents, and technical references.
5. **Real-time Collaboration**: Enable collaborative analysis with AI-powered notifications and insights.
6. **Workshop Preparation Mode**: Generate preparation materials to enhance HAZOP workshop effectiveness.

## Setup

### Requirements

- Python 3.8+
- Node.js 14+
- PostgreSQL 13+
- Google Gemini API Key (Pro or higher tier recommended)

### Configuration

1. Add your Gemini API key to the backend `.env` file:

```
GEMINI_API_KEY=your_gemini_api_key
```

2. Configure Gemini service settings in `backend/app/config/settings.py`:

```python
GEMINI_SETTINGS = {
    "model": "gemini-1.5-pro",
    "temperature": 0.2,
    "top_p": 0.95,
    "max_output_tokens": 2048,
}
```

## Features

### AI Suggestion Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/gemini/suggest-causes` | Generate AI suggestions for causes of a deviation |
| `/api/gemini/suggest-consequences` | Generate AI suggestions for consequences of a deviation or cause |
| `/api/gemini/suggest-safeguards` | Generate AI suggestions for safeguards to mitigate risks |
| `/api/gemini/complete-analysis` | Generate a complete analysis with causes, consequences, and safeguards |
| `/api/gemini/suggest-risk-assessment` | Get AI suggestions for likelihood and severity ratings |
| `/api/gemini/evaluate-safeguard-effectiveness` | Evaluate the effectiveness of a safeguard and get improvement suggestions |
| `/api/gemini/contextual-knowledge` | Get relevant regulations, incidents, and technical references |
| `/api/gemini/workshop-preparation` | Generate preparation materials for HAZOP workshops |

### Frontend Components

| Component | Description |
|-----------|-------------|
| `GeminiInsightsPanel` | Displays AI-generated suggestions during HAZOP analysis |
| `SmartRiskRecalculator` | Provides AI-informed risk recalculation suggestions |
| `SafeguardEffectivenessEvaluator` | Evaluates safeguards and provides improvement suggestions |
| `ContextualKnowledgePanel` | Displays contextual knowledge relevant to the current analysis |
| `CollaborationPanel` | Enables real-time collaborative analysis with AI insights |
| `WorkshopPreparationPanel` | Provides workshop preparation materials and intelligence |

## Usage

### AI Suggestions

The GeminiInsightsPanel appears during HAZOP analysis and provides real-time AI suggestions. Click the "Add" button to incorporate suggestions directly into your analysis.

### Smart Risk Assessment

When performing a risk assessment, use the SmartRiskRecalculator to get AI-informed suggestions for likelihood and severity ratings based on historical data and industry norms.

### Safeguard Effectiveness

For each safeguard, you can use the SafeguardEffectivenessEvaluator to analyze its effectiveness and get improvement suggestions.

### Contextual Knowledge

The ContextualKnowledgePanel provides relevant regulations, industry incidents, and technical references for the current node or deviation.

### Workshop Preparation

1. Navigate to the Workshop Preparation mode
2. Click "Generate Workshop Materials"
3. Review the AI-generated high-risk areas, suggested questions, similar nodes, and reference materials
4. Use these materials to enhance your HAZOP workshop

## Testing

Run the integration tests to verify that the Gemini integration is working correctly:

```bash
cd tests
cp .env.example .env
# Update the .env file with your test credentials
python test_gemini_integration.py
```

## Troubleshooting

### API Key Issues

If you encounter "Authentication failed" errors, verify your Gemini API key is correct and has sufficient permissions.

### Model Limitations

- The system uses the Gemini 1.5 Pro model which has token limits. Very complex analyses may need to be broken down into smaller components.
- Response times vary based on the complexity of the request and Gemini API load.

### Network Errors

If the application fails to connect to the Gemini API, check your network connection and firewall settings.

## Future Enhancements

- Integration with process simulation data for more accurate recommendations
- Enhanced knowledge base with industry-specific regulations and incidents
- Improved real-time collaboration features with multi-user editing
- Extended reporting capabilities with AI-generated executive summaries