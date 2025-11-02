import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.infrastructure.ai.gemini_client import GeminiClient
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

async def main():
    """Simple interactive test"""
    logger.info("🚀 Starting Gemini Client Test")
    
    # Initialize client
    client = GeminiClient()
    logger.info("✅ Client initialized")
    
    # Test 1: Simple JSON request
    print("\n" + "="*50)
    print("TEST 1: Safety Score for Tokyo")
    print("="*50)
    
    result = await client.generate_json(
        prompt="""
        Rate the safety of Tokyo, Japan for tourists.
        Return JSON with: safety_score (0-100), risk_level, and top 3 tips.
        
        Format:
        {
            "safety_score": 95,
            "risk_level": "low",
            "tips": ["tip1", "tip2", "tip3"]
        }
        """,
        system_context="You are a travel safety expert. Respond in JSON."
    )
    
    print(f"\n📊 Result:")
    import json
    print(json.dumps(result, indent=2))
    
    # Test 2: Simple text
    print("\n" + "="*50)
    print("TEST 2: Plain Text Response")
    print("="*50)
    
    text_result = await client.generate_text(
        "Give me one safety tip for traveling in Europe."
    )
    
    print(f"\n💡 Result: {text_result}")
    
    logger.info("🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())