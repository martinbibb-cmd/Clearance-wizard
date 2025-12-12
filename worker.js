/**
 * Cloudflare Worker for AI-Powered Clearance Verification
 * Supports Gemini, OpenAI, and Claude with automatic fallback
 *
 * Environment Variables Required:
 * - GEMINI_API_KEY
 * - OPENAI_API_KEY
 * - ANTHROPIC_API_KEY
 */

export default {
  async fetch(request, env) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      const data = await request.json();
      const { provider, image, appliance, clearances, task } = data;

      if (!image || !appliance || !clearances) {
        return new Response(
          JSON.stringify({ error: 'Missing required fields' }),
          { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
      }

      let result;

      switch (provider) {
        case 'gemini':
          result = await analyzeWithGemini(env, image, appliance, clearances);
          break;
        case 'openai':
          result = await analyzeWithOpenAI(env, image, appliance, clearances);
          break;
        case 'claude':
          result = await analyzeWithClaude(env, image, appliance, clearances);
          break;
        default:
          return new Response(
            JSON.stringify({ error: 'Invalid provider' }),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
          );
      }

      return new Response(JSON.stringify(result), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });

    } catch (error) {
      console.error('Worker error:', error);
      return new Response(
        JSON.stringify({ error: error.message }),
        {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          }
        }
      );
    }
  },
};

// ==========================================
// GEMINI INTEGRATION
// ==========================================
async function analyzeWithGemini(env, image, appliance, clearances) {
  const apiKey = env.GEMINI_API_KEY;
  if (!apiKey) throw new Error('Gemini API key not configured');

  const prompt = generatePrompt(appliance, clearances);

  // Remove data URL prefix if present
  const base64Image = image.replace(/^data:image\/(png|jpeg|jpg);base64,/, '');

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{
          parts: [
            { text: prompt },
            {
              inline_data: {
                mime_type: 'image/jpeg',
                data: base64Image
              }
            }
          ]
        }],
        generationConfig: {
          temperature: 0.4,
          topK: 32,
          topP: 1,
          maxOutputTokens: 2048,
        }
      })
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Gemini API error: ${error}`);
  }

  const result = await response.json();
  const text = result.candidates[0].content.parts[0].text;

  // Extract JSON from response (handle markdown code blocks)
  return parseAIResponse(text);
}

// ==========================================
// OPENAI INTEGRATION
// ==========================================
async function analyzeWithOpenAI(env, image, appliance, clearances) {
  const apiKey = env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OpenAI API key not configured');

  const prompt = generatePrompt(appliance, clearances);

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o',
      messages: [
        {
          role: 'user',
          content: [
            { type: 'text', text: prompt },
            { type: 'image_url', image_url: { url: image } }
          ]
        }
      ],
      max_tokens: 2048,
      temperature: 0.4,
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenAI API error: ${error}`);
  }

  const result = await response.json();
  const text = result.choices[0].message.content;

  return parseAIResponse(text);
}

// ==========================================
// CLAUDE INTEGRATION
// ==========================================
async function analyzeWithClaude(env, image, appliance, clearances) {
  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) throw new Error('Claude API key not configured');

  const prompt = generatePrompt(appliance, clearances);

  // Remove data URL prefix and get mime type
  const matches = image.match(/^data:image\/(png|jpeg|jpg);base64,(.+)$/);
  const mimeType = matches ? `image/${matches[1]}` : 'image/jpeg';
  const base64Image = matches ? matches[2] : image;

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 2048,
      temperature: 0.4,
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'image',
              source: {
                type: 'base64',
                media_type: mimeType,
                data: base64Image,
              },
            },
            {
              type: 'text',
              text: prompt,
            },
          ],
        },
      ],
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Claude API error: ${error}`);
  }

  const result = await response.json();
  const text = result.content[0].text;

  return parseAIResponse(text);
}

// ==========================================
// SHARED UTILITIES
// ==========================================
function generatePrompt(appliance, clearances) {
  const clearanceText = Object.entries(clearances)
    .map(([side, distance]) => `- ${side.toUpperCase()}: ${distance}mm minimum`)
    .join('\n');

  return `You are an expert heating engineer analyzing a clearance installation photo.

APPLIANCE DETAILS:
- Type: ${appliance.category}
- Model: ${appliance.label}
- Dimensions: ${appliance.w}mm (W) × ${appliance.h}mm (H) × ${appliance.d}mm (D)

REQUIRED CLEARANCES:
${clearanceText}

ANALYSIS REQUIRED:
1. Detect all objects/obstacles in the scene (walls, windows, doors, furniture, electrical outlets, other appliances, cupboards, radiators, pipes, etc.)
2. Estimate the distance from the appliance position (shown by the AR overlay) to each detected object
3. Identify potential clearance violations
4. For each detected object, provide:
   - Object type/name (e.g., "window", "cupboard", "wall", "electrical outlet")
   - Estimated position relative to appliance (top/bottom/left/right/front)
   - Estimated distance in mm
   - Whether it violates clearance requirements
   - Confidence level (0-100%)
   - Any relevant notes

5. Overall assessment: "pass", "fail", or "warning"
6. List any critical violations that must be addressed
7. List any warnings or recommendations

IMPORTANT: Be conservative with clearances. If uncertain, mark as a potential violation.

Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):
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
    }
  ],
  "overallStatus": "pass",
  "violations": [],
  "warnings": [],
  "recommendations": ["Consider additional ventilation"]
}`;
}

function parseAIResponse(text) {
  try {
    // Remove markdown code blocks if present
    let cleanText = text.trim();
    if (cleanText.startsWith('```json')) {
      cleanText = cleanText.replace(/^```json\n/, '').replace(/\n```$/, '');
    } else if (cleanText.startsWith('```')) {
      cleanText = cleanText.replace(/^```\n/, '').replace(/\n```$/, '');
    }

    const parsed = JSON.parse(cleanText);

    // Validate structure
    if (!parsed.detectedObjects || !Array.isArray(parsed.detectedObjects)) {
      parsed.detectedObjects = [];
    }
    if (!parsed.overallStatus) {
      parsed.overallStatus = 'warning';
    }
    if (!parsed.violations) {
      parsed.violations = [];
    }
    if (!parsed.warnings) {
      parsed.warnings = [];
    }
    if (!parsed.recommendations) {
      parsed.recommendations = [];
    }

    return parsed;

  } catch (error) {
    console.error('Failed to parse AI response:', text);
    // Return a safe fallback structure
    return {
      detectedObjects: [],
      overallStatus: 'warning',
      violations: ['Unable to analyze image. Please try again.'],
      warnings: [],
      recommendations: []
    };
  }
}
