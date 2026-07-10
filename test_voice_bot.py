#!/usr/bin/env python
"""
Test script for PartyPe voice bot
"""

import asyncio
from voice_bot import SimpleVoiceBot

async def test_voice_bot():
    bot = SimpleVoiceBot()
    print("=== PartyPe Voice Bot Test ===\n")
    
    test_cases = [
        "show menu",
        "I want to order butter chicken and garlic naan",
        "what's in my cart",
        "add pepperoni pizza",
        "what's in my cart",
        "remove garlic naan",
        "what's in my cart",
        "cancel everything",
        "what's in my cart"
    ]
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"Test {i}: You: {user_input}")
        response = await bot.process_input(user_input)
        print(f"Bot: {response}\n")
        # Small delay for readability
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(test_voice_bot())
