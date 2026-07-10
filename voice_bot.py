#!/usr/bin/env python
"""
Simple voice bot prototype for PartyPe food ordering
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVoiceBot:
    def __init__(self):
        self.menu = {
            1: {"name": "Butter Chicken", "price": 299, "category": "Main Course"},
            2: {"name": "Garlic Naan", "price": 89, "category": "Bread"},
            3: {"name": "Vegetable Biryani", "price": 249, "category": "Main Course"},
            4: {"name": "Margherita Pizza", "price": 349, "category": "Pizza"},
            5: {"name": "Pepperoni Pizza", "price": 399, "category": "Pizza"},
            6: {"name": "Caesar Salad", "price": 199, "category": "Salad"}
        }
        self.current_order = []

    async def process_input(self, text: str) -> str:
        """Process text input (simulating speech-to-text) and return response"""
        text = text.lower().strip()
        
        # Intent detection
        if any(word in text for word in ["menu", "show", "see"]):
            return self.get_menu()
        elif any(word in text for word in ["order", "want", "get"]):
            return self.handle_order(text)
        elif any(word in text for word in ["cart", "order status", "what's in"]):
            return self.get_order_status()
        elif any(word in text for word in ["cancel", "remove"]):
            return self.cancel_order(text)
        elif any(word in text for word in ["help", "agent", "human"]):
            return "Connecting you to a human agent..."
        else:
            return "Sorry, I didn't understand. You can say 'show menu', 'I want to order butter chicken', or 'what's in my cart'."

    def get_menu(self) -> str:
        response = "Here's our menu:\n"
        categories = {}
        for item_id, item in self.menu.items():
            cat = item["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        for category, items in categories.items():
            response += f"\n{category}:\n"
            for item in items:
                response += f"  - {item['name']}: ₹{item['price']}\n"
        return response

    def handle_order(self, text: str) -> str:
        # Simple item extraction
        items_added = []
        total = 0
        
        item_map = {
            "butter chicken": 1,
            "garlic naan": 2,
            "vegetable biryani": 3,
            "margherita": 4,
            "pepperoni": 5,
            "caesar salad": 6
        }
        
        for item_name, item_id in item_map.items():
            if item_name in text:
                item = self.menu[item_id]
                self.current_order.append(item)
                items_added.append(item["name"])
                total += item["price"]
        
        if items_added:
            response = f"Added {', '.join(items_added)} to your order. "
            response += f"Current total: ₹{total}. "
            response += "Add more items or proceed to checkout?"
            return response
        else:
            return "I didn't recognize any items. Please try again with menu item names."

    def get_order_status(self) -> str:
        if not self.current_order:
            return "Your cart is empty. Would you like to see the menu?"
        
        total = sum(item["price"] for item in self.current_order)
        items = ", ".join([item["name"] for item in self.current_order])
        return f"Your order: {items}. Total: ₹{total}. Proceed to checkout?"

    def cancel_order(self, text: str) -> str:
        if not self.current_order:
            return "Your cart is already empty."

        if "all" in text or "everything" in text:
            self.current_order.clear()
            return "Cleared your entire order."

        # Remove specific items
        removed = []
        item_map = {
            "butter chicken": 1,
            "garlic naan": 2,
            "vegetable biryani": 3,
            "margherita": 4,
            "pepperoni": 5,
            "caesar salad": 6
        }

        for item_name, item_id in item_map.items():
            if item_name in text:
                # Find and remove matching items by name
                for item in self.current_order[:]:
                    if item["name"].lower() == item_name:
                        self.current_order.remove(item)
                        removed.append(item["name"])

        if removed:
            return f"Removed {', '.join(removed)} from your order."
        else:
            return "I didn't find those items in your order."

async def demo():
    bot = SimpleVoiceBot()
    print("=== PartyPe Voice Bot Demo ===")
    print("Type your message (or 'quit' to exit)")
    print("Try: 'show menu', 'I want to order butter chicken', 'what's in my cart'")
    print()
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            break
        
        response = await bot.process_input(user_input)
        print(f"Bot: {response}\n")

if __name__ == "__main__":
    asyncio.run(demo())