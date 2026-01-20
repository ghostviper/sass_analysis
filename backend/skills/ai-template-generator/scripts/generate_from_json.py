#!/usr/bin/env python3
"""
Generate templates from JSON parameter file
"""

import sys
import json
import asyncio
from pathlib import Path

# Import the main generation function
from generate_template import generate_templates, extract_python_code


async def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_from_json.py <params.json> [output.py]")
        sys.exit(1)
    
    params_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    # Load parameters
    with open(params_file, 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    observation = params['observation']
    guidance = params['guidance']
    count = params.get('count', 3)
    model = params.get('model', 'gpt-4o')
    api_url = params.get('api_url', 'http://localhost:8001')
    
    print(f"🤖 Generating {count} templates...")
    print(f"📊 Observation: {observation[:50]}...")
    print(f"💡 Guidance: {guidance[:50]}...")
    print()
    
    # Generate
    response = await generate_templates(
        observation=observation,
        guidance=guidance,
        count=count,
        model=model,
        api_url=api_url
    )
    
    # Extract code
    code = extract_python_code(response)
    
    # Output
    if output_file:
        output_file.write_text(code, encoding='utf-8')
        print(f"✅ Templates saved to: {output_file}")
    else:
        print("=" * 80)
        print(code)
        print("=" * 80)
    
    print()
    print("✨ Generation complete!")


if __name__ == "__main__":
    asyncio.run(main())
