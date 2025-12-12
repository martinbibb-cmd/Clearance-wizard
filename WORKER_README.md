# Clearance Wizard AI Worker

This Cloudflare Worker provides AI-powered clearance verification for the Clearance Wizard AR application. It supports multiple AI providers with automatic fallback: Gemini → OpenAI → Claude.

## Features

- **Multi-Provider AI**: Automatic fallback between Gemini, OpenAI, and Claude
- **Object Detection**: Identifies walls, windows, doors, furniture, outlets, and obstacles
- **Distance Estimation**: Estimates distances from appliance to detected objects
- **Clearance Verification**: Validates against manufacturer requirements
- **CORS Support**: Allows requests from any origin

## Setup

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

### 2. Login to Cloudflare

```bash
wrangler login
```

### 3. Set API Keys

You need at least one of these API keys (all three recommended for best reliability):

```bash
# Gemini API Key (Google AI Studio)
wrangler secret put GEMINI_API_KEY

# OpenAI API Key
wrangler secret put OPENAI_API_KEY

# Anthropic API Key (Claude)
wrangler secret put ANTHROPIC_API_KEY
```

### 4. Deploy the Worker

```bash
wrangler deploy
```

The worker will be available at: `https://clearance-wizard-ai.YOUR-SUBDOMAIN.workers.dev`

## Getting API Keys

### Gemini (Google AI Studio)
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key

### OpenAI
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key
4. Ensure you have GPT-4 Vision access

### Claude (Anthropic)
1. Visit https://console.anthropic.com/
2. Create an API key
3. Copy the key

## API Endpoint

### POST Request

```bash
curl -X POST https://clearance.martinbibb.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "image": "data:image/jpeg;base64,...",
    "appliance": {
      "category": "boiler",
      "label": "Worcester 4000",
      "w": 400,
      "h": 724,
      "d": 310
    },
    "clearances": {
      "top": 170,
      "bottom": 200,
      "left": 5,
      "right": 5,
      "front": 600
    },
    "task": "clearance_verification"
  }'
```

### Response Format

```json
{
  "detectedObjects": [
    {
      "type": "window",
      "position": "left",
      "distance": 800,
      "requiredClearance": 300,
      "status": "pass",
      "confidence": 85,
      "notes": "Double-glazed window, sufficient clearance"
    },
    {
      "type": "cupboard",
      "position": "right",
      "distance": 150,
      "requiredClearance": 300,
      "status": "fail",
      "confidence": 90,
      "notes": "Kitchen cupboard too close to appliance"
    }
  ],
  "overallStatus": "fail",
  "violations": [
    "Cupboard on right side is 150mm away, requires minimum 300mm clearance"
  ],
  "warnings": [
    "Ensure adequate ventilation in the room"
  ],
  "recommendations": [
    "Remove or relocate cupboard before installation",
    "Consider repositioning appliance to maintain clearances"
  ]
}
```

## Provider Fallback Logic

The worker tries providers in this order:

1. **Gemini 2.0 Flash** (fastest, most cost-effective)
   - If fails → try OpenAI

2. **GPT-4 Vision** (reliable, good accuracy)
   - If fails → try Claude

3. **Claude 3.5 Sonnet** (highest accuracy, most conservative)
   - If fails → return error

## Cost Considerations

### Gemini
- **Model**: gemini-2.0-flash-exp
- **Cost**: Free tier available, then ~$0.00035 per request
- **Speed**: ~2-3 seconds

### OpenAI
- **Model**: gpt-4o
- **Cost**: ~$0.01 per request
- **Speed**: ~3-5 seconds

### Claude
- **Model**: claude-3-5-sonnet-20241022
- **Cost**: ~$0.015 per request
- **Speed**: ~4-6 seconds

**Recommendation**: Use Gemini for development and production. Add OpenAI/Claude as backups.

## Monitoring

View logs in real-time:

```bash
wrangler tail
```

## Troubleshooting

### "Provider failed with status 401"
- Check that API key is set correctly: `wrangler secret list`
- Verify API key is valid in respective provider's dashboard

### "All AI providers failed"
- Ensure at least one API key is configured
- Check worker logs: `wrangler tail`
- Verify API quotas/billing are active

### "Image too large" error
- Client compresses images to JPEG quality 0.8
- Max recommended size: 4MB
- Cloudflare Worker request limit: 100MB

## Security

- API keys are stored as encrypted secrets in Cloudflare
- Keys are never exposed in client-side code
- CORS is configured to allow all origins (adjust if needed)
- No data is stored or logged (except ephemeral request logs)

## Development

Test locally:

```bash
wrangler dev
```

Then update client-side endpoint to: `http://localhost:8787`

## Updates

To update the worker:

```bash
wrangler deploy
```

Changes are deployed globally within seconds.
