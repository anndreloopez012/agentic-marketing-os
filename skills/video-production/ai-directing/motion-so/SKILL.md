---
name: motion-so
description: Frontier AI agent and studio for motion design (motion.so by Mosaic). Generates launch videos, product demos, explainers, logo animations, and social ads from text prompts or brand URLs. Integrates via MCP (https://mcp.motion.so/mcp).
metadata:
  tags: motion, video, ai-video, motion-design, mcp, launch-videos, product-demos, explainers
---

# Motion.so — Frontier AI for Motion Design

Motion (`https://motion.so`, by Mosaic) is an AI agent and creative studio for motion design that generates, animates, and renders videos directly from text prompts, URLs, brand assets, or references.

## Ecosystem Comparison: Hyperframes vs. Remotion vs. Motion.so

| Tool | Core Engine | Authoring Model | Best For |
|---|---|---|---|
| **Hyperframes** | HTML, CSS, GSAP | Agent-native code (HTML/GSAP) | Code-driven programmatic motion graphics, short assets, animated charts, maps |
| **Remotion** | React & Web APIs | React components (`useCurrentFrame`) | Scalable programmatic video platforms, complex React UI in video |
| **Motion.so** | AI Motion Agent (Cloud) | Natural language prompt / MCP | Fast high-fidelity launch videos, product demos, Vox-style explainers, logo reveals |

## MCP Connection (Model Context Protocol)

Motion provides a native MCP endpoint that can be connected to Claude Desktop, ChatGPT, Cursor, or any MCP client:

- **Server URL:** `https://mcp.motion.so/mcp`
- **Authentication:** OAuth 2.1 flow in browser (or device flow via `https://motion.so/device`)
- **No API key needed:** Automatically links your Motion account and credits.

### Setup in Claude Desktop
In Claude Desktop configuration (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "motion": {
      "url": "https://mcp.motion.so/mcp"
    }
  }
}
```

### Setup in Cursor / AI Agents
Add custom MCP connector:
- Name: `motion`
- Type: `SSE` or `HTTP`
- URL: `https://mcp.motion.so/mcp`

## Capabilities & Video Types

1. **Launch Videos (`/solutions/launch-videos`):**
   - Cinematic product launches, bold typography, dark aesthetic, punchy soundtrack, voiceover.
   - Example prompt: `Make a 30-second launch video for [Product Name], bold type, dark, kinetic, confident voiceover.`
2. **Product Demos (`/solutions/product-demos`):**
   - Scene-by-scene software walk-throughs with smooth cursor interactions, feature callouts, and UI highlights.
3. **Deep-dive Explainers (`/solutions/explainers`):**
   - Vox-style educational videos, animated data-viz, timelines, narrative storytelling.
4. **Article / Newsletter to Video (`/solutions/article-to-video`):**
   - Turn blog posts, PRs, or newsletters into social clips.
5. **Logo Animations & Ident:**
   - Kinetic brand reveals, SVG path draw, intro/outro stingers.

## Prompting Best Practices for Motion.so

- **Specify Duration & Aspect Ratio:** Always specify duration (`15s`, `30s`, `60s`) and aspect ratio (`16:9` widescreen, `9:16` vertical reels/shorts, `1:1` square).
- **Define the Tone & Style:** e.g., "minimalist Apple-style", "kinetic and fast-paced", "documentary / Vox style", "dark cyber / sleek".
- **Provide Brand Assets & URLs:** Include company website URLs, hex brand colors, or vector logo URLs.
- **Use Plan Mode:** When drafting complex videos, instruct Motion to outline the storyboard and scene progression before rendering.
- **Iterative Edits:** Motion allows scene-by-scene chat revisions without re-rendering unaffected scenes.
