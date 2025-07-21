# Shopify Integration

Transform your Shopify store with interactive bitHuman avatars that can serve as virtual sales assistants, product demonstrators, and customer service representatives.

## Overview

bitHuman + Shopify enables:
- **Virtual Sales Assistants** - AI-powered shopping guidance
- **Product Demonstrations** - Avatar-led product showcases
- **Customer Support** - Real-time assistance with orders and inquiries
- **Personalized Shopping** - Tailored recommendations and experiences
- **Interactive Storefronts** - Engaging, human-like interactions

## Prerequisites

- ✅ Active Shopify store (any plan)
- ✅ [bitHuman SDK access](../getting-started/installation.md)
- ✅ [Validated API credentials](../getting-started/validate-api.md)
- ✅ Basic knowledge of Shopify development

## Setup Options

### Option 1: Shopify App (Recommended)

The easiest way to add bitHuman avatars to your store.

#### Install the App

1. Visit [Shopify App Store](https://apps.shopify.com)
2. Search for "bitHuman Virtual Assistant"
3. Click "Add app" and follow installation steps
4. Connect your bitHuman account during setup

#### Configure Your Avatar

```javascript
// Configure in your Shopify admin
{
  "avatar": {
    "model_id": "your_model_id",
    "personality": "friendly_sales_assistant",
    "knowledge_base": {
      "products": true,
      "policies": true,
      "faq": true
    },
    "features": {
      "product_recommendations": true,
      "order_tracking": true,
      "inventory_status": true
    }
  }
}
```

### Option 2: Custom Implementation

For advanced customization and control.

#### Install Dependencies

```bash
# Install required packages
npm install @shopify/polaris @shopify/app-bridge bithumanjs

# Or for server-side integration
pip install shopify-python-api bithuman requests
```

#### Basic Widget Implementation

```html
<!-- Add to your theme's layout/theme.liquid -->
<div id="bithuman-avatar-widget">
  <div id="avatar-container"></div>
  <div id="chat-interface">
    <div id="chat-messages"></div>
    <input type="text" id="chat-input" placeholder="Ask me anything about our products...">
    <button id="send-button">Send</button>
  </div>
</div>

<script>
class ShopifyAvatarWidget {
  constructor() {
    this.avatar = null;
    this.sessionId = this.generateSessionId();
    this.productData = null;
    this.customerData = null;
  }

  async initialize() {
    // Load product and customer data
    await this.loadShopifyData();
    
    // Initialize bitHuman avatar
    this.avatar = new BitHumanAvatar({
      containerId: 'avatar-container',
      apiKey: '{{ settings.bithuman_api_key }}',
      modelId: '{{ settings.bithuman_model_id }}',
      personality: 'sales_assistant',
      context: {
        store_name: '{{ shop.name }}',
        products: this.productData,
        customer: this.customerData
      }
    });

    await this.avatar.initialize();
    this.setupEventHandlers();
    
    // Greet the customer
    await this.avatar.speak(this.generateGreeting());
  }

  async loadShopifyData() {
    // Load current product if on product page
    if (window.location.pathname.includes('/products/')) {
      this.productData = await this.getCurrentProduct();
    }
    
    // Load customer data if logged in
    if (window.Shopify.customer) {
      this.customerData = window.Shopify.customer;
    }
  }

  async getCurrentProduct() {
    const productHandle = window.location.pathname.split('/products/')[1];
    const response = await fetch(`/products/${productHandle}.js`);
    return await response.json();
  }

  generateGreeting() {
    const greetings = [
      `Welcome to ${Shopify.shop.name}! I'm here to help you find exactly what you're looking for.`,
      `Hi there! I'm your virtual shopping assistant. How can I help you today?`,
      `Welcome! I'm here to answer any questions about our products or help with your order.`
    ];
    
    return greetings[Math.floor(Math.random() * greetings.length)];
  }

  setupEventHandlers() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');

    sendButton.addEventListener('click', () => this.sendMessage());
    
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.sendMessage();
      }
    });
  }

  async sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Display user message
    this.addMessageToChat('user', message);
    input.value = '';
    
    // Process with avatar
    const response = await this.processUserMessage(message);
    
    // Display avatar response
    this.addMessageToChat('avatar', response.text);
    await this.avatar.speak(response.text);
    
    // Handle any actions (e.g., product recommendations)
    if (response.actions) {
      await this.handleActions(response.actions);
    }
  }

  async processUserMessage(message) {
    // Send to bitHuman processing endpoint
    const response = await fetch('/apps/bithuman/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        context: {
          session_id: this.sessionId,
          current_product: this.productData,
          customer: this.customerData,
          cart: this.getCartData()
        }
      })
    });
    
    return await response.json();
  }

  getCartData() {
    return fetch('/cart.js').then(r => r.json());
  }

  addMessageToChat(sender, message) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async handleActions(actions) {
    for (const action of actions) {
      switch (action.type) {
        case 'show_product':
          await this.showProduct(action.product_id);
          break;
        case 'add_to_cart':
          await this.addToCart(action.variant_id, action.quantity);
          break;
        case 'show_recommendations':
          await this.showRecommendations(action.products);
          break;
      }
    }
  }

  async showProduct(productId) {
    // Navigate to product page or show in modal
    window.location.href = `/products/${productId}`;
  }

  async addToCart(variantId, quantity = 1) {
    const response = await fetch('/cart/add.js', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id: variantId,
        quantity: quantity
      })
    });
    
    if (response.ok) {
      // Update cart UI
      document.dispatchEvent(new CustomEvent('cart:updated'));
      this.addMessageToChat('avatar', 'Great! I\'ve added that to your cart.');
    }
  }

  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  const widget = new ShopifyAvatarWidget();
  widget.initialize();
});
</script>

<style>
#bithuman-avatar-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 350px;
  height: 500px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

#avatar-container {
  height: 200px;
  background: #f8f9fa;
  border-radius: 10px 10px 0 0;
  position: relative;
}

#chat-interface {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 15px;
}

#chat-messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 5px;
}

.message {
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 15px;
  max-width: 80%;
}

.user-message {
  background: #007bff;
  color: white;
  margin-left: auto;
}

.avatar-message {
  background: #e9ecef;
  color: #333;
}

#chat-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
}

#send-button {
  margin-left: 10px;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}
</style>

## Backend Processing

### Shopify Webhook Handler

```python
# shopify_webhook_handler.py
import os
import json
import asyncio
from flask import Flask, request, jsonify
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk
import shopify

app = Flask(__name__)

class ShopifyAvatarProcessor:
    def __init__(self):
        self.bithuman_runtime = None
        self.shopify_session = None
        
    async def initialize(self):
        """Initialize bitHuman and Shopify connections"""
        # Initialize bitHuman
        self.bithuman_runtime = await AsyncBithuman.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
        )
        
        # Initialize Shopify
        shopify.ShopifyResource.set_site(
            f"https://{os.getenv('SHOPIFY_API_KEY')}:{os.getenv('SHOPIFY_API_SECRET')}"
            f"@{os.getenv('SHOPIFY_SHOP_DOMAIN')}/admin/api/2023-10"
        )
    
    async def process_customer_message(self, message: str, context: dict):
        """Process customer message and generate avatar response"""
        # Analyze intent
        intent = await self.analyze_intent(message, context)
        
        # Generate appropriate response
        response_text = await self.generate_response(intent, context)
        
        # Process any required actions
        actions = await self.determine_actions(intent, context)
        
        return {
            'text': response_text,
            'actions': actions,
            'intent': intent
        }
    
    async def analyze_intent(self, message: str, context: dict):
        """Analyze customer intent from message"""
        message_lower = message.lower()
        
        # Product inquiry
        if any(word in message_lower for word in ['product', 'item', 'price', 'cost', 'buy']):
            if context.get('current_product'):
                return {'type': 'product_inquiry', 'product': context['current_product']}
            else:
                return {'type': 'product_search', 'query': message}
        
        # Order tracking
        elif any(word in message_lower for word in ['order', 'track', 'shipping', 'delivery']):
            return {'type': 'order_inquiry', 'customer': context.get('customer')}
        
        # Size/fit questions
        elif any(word in message_lower for word in ['size', 'fit', 'sizing', 'measurements']):
            return {'type': 'sizing_help', 'product': context.get('current_product')}
        
        # Recommendations
        elif any(word in message_lower for word in ['recommend', 'suggest', 'similar', 'like']):
            return {'type': 'recommendation_request', 'context': context}
        
        # General support
        else:
            return {'type': 'general_support', 'query': message}
    
    async def generate_response(self, intent: dict, context: dict):
        """Generate appropriate response based on intent"""
        if intent['type'] == 'product_inquiry':
            product = intent['product']
            return f"This is our {product['title']}! It's priced at {product['price']} and {product['description'][:100]}... Would you like to know more about its features or add it to your cart?"
        
        elif intent['type'] == 'product_search':
            products = await self.search_products(intent['query'])
            if products:
                return f"I found some great products for you! Let me show you our {products[0]['title']} - it's one of our bestsellers."
            else:
                return "I couldn't find any products matching your search. Could you try a different keyword, or would you like me to show you our featured items?"
        
        elif intent['type'] == 'order_inquiry':
            customer = intent.get('customer')
            if customer:
                orders = await self.get_customer_orders(customer['id'])
                if orders:
                    latest_order = orders[0]
                    return f"Your most recent order #{latest_order['order_number']} is currently {latest_order['fulfillment_status']}. Would you like me to check the tracking details?"
                else:
                    return "I don't see any recent orders for your account. Is there anything else I can help you with?"
            else:
                return "I'd be happy to help you track your order! Could you please log in to your account or provide your order number?"
        
        elif intent['type'] == 'sizing_help':
            return "I'd be happy to help you find the right size! Our size guide shows detailed measurements for each size. Would you like me to show you the size chart, or do you have specific measurements you'd like me to help you match?"
        
        elif intent['type'] == 'recommendation_request':
            return "I'd love to help you find something perfect! Based on what you're looking for, I have some great recommendations. Let me show you a few options that I think you'll love."
        
        else:
            return "I'm here to help! Feel free to ask me about our products, your orders, sizing, or anything else. What would you like to know?"
    
    async def determine_actions(self, intent: dict, context: dict):
        """Determine what actions to take based on intent"""
        actions = []
        
        if intent['type'] == 'product_search':
            products = await self.search_products(intent['query'])
            actions.append({
                'type': 'show_recommendations',
                'products': products[:3]  # Show top 3 results
            })
        
        elif intent['type'] == 'recommendation_request':
            recommendations = await self.get_recommendations(context)
            actions.append({
                'type': 'show_recommendations',
                'products': recommendations
            })
        
        return actions
    
    async def search_products(self, query: str):
        """Search products in Shopify"""
        try:
            products = shopify.Product.find(title=query, limit=10)
            return [self.format_product(p) for p in products]
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    async def get_customer_orders(self, customer_id: str):
        """Get customer orders from Shopify"""
        try:
            orders = shopify.Order.find(customer_id=customer_id, limit=5)
            return [self.format_order(o) for o in orders]
        except Exception as e:
            print(f"Error getting orders: {e}")
            return []
    
    async def get_recommendations(self, context: dict):
        """Generate product recommendations"""
        # Simple recommendation logic - in production, use ML/AI
        try:
            if context.get('current_product'):
                # Recommend related products
                current_product = context['current_product']
                related = shopify.Product.find(
                    product_type=current_product.get('product_type'),
                    limit=3
                )
                return [self.format_product(p) for p in related]
            else:
                # Recommend featured products
                featured = shopify.Product.find(limit=3)
                return [self.format_product(p) for p in featured]
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def format_product(self, product):
        """Format product data for frontend"""
        return {
            'id': product.id,
            'title': product.title,
            'price': str(product.variants[0].price) if product.variants else 'N/A',
            'description': product.body_html or '',
            'image': product.images[0].src if product.images else None,
            'handle': product.handle
        }
    
    def format_order(self, order):
        """Format order data for frontend"""
        return {
            'id': order.id,
            'order_number': order.order_number,
            'total_price': str(order.total_price),
            'fulfillment_status': order.fulfillment_status or 'pending',
            'created_at': str(order.created_at)
        }

# Initialize processor
processor = ShopifyAvatarProcessor()

@app.before_first_request
async def startup():
    await processor.initialize()

@app.route('/apps/bithuman/process', methods=['POST'])
async def process_message():
    """Process customer message"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', {})
        
        response = await processor.process_customer_message(message, context)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/apps/bithuman/webhook', methods=['POST'])
def handle_webhook():
    """Handle Shopify webhooks"""
    try:
        # Verify webhook (implement HMAC verification)
        webhook_payload = request.get_json()
        webhook_topic = request.headers.get('X-Shopify-Topic')
        
        # Handle different webhook types
        if webhook_topic == 'orders/create':
            # New order created - could trigger avatar notification
            pass
        elif webhook_topic == 'products/update':
            # Product updated - refresh product cache
            pass
            
        return '', 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## Advanced Features

### Product Demonstration Mode

```javascript
// product_demo.js
class ProductDemonstrationMode {
  constructor(avatar, productData) {
    this.avatar = avatar;
    this.product = productData;
    this.demoSteps = this.generateDemoSteps();
    this.currentStep = 0;
  }

  generateDemoSteps() {
    const steps = [
      {
        text: `Let me show you the amazing features of our ${this.product.title}.`,
        action: 'highlight_product',
        duration: 3000
      },
      {
        text: `This product is made with high-quality materials and has received excellent customer reviews.`,
        action: 'show_reviews',
        duration: 4000
      }
    ];

    // Add feature-specific steps based on product type
    if (this.product.product_type === 'clothing') {
      steps.push({
        text: `Available in multiple sizes and colors to fit your style perfectly.`,
        action: 'show_variants',
        duration: 3000
      });
    }

    steps.push({
      text: `Would you like to add this to your cart or see similar products?`,
      action: 'show_cta',
      duration: 2000
    });

    return steps;
  }

  async startDemo() {
    this.currentStep = 0;
    await this.playStep();
  }

  async playStep() {
    if (this.currentStep >= this.demoSteps.length) {
      await this.completDemo();
      return;
    }

    const step = this.demoSteps[this.currentStep];
    
    // Make avatar speak
    await this.avatar.speak(step.text);
    
    // Execute action
    await this.executeAction(step.action);
    
    // Wait for step duration
    setTimeout(() => {
      this.currentStep++;
      this.playStep();
    }, step.duration);
  }

  async executeAction(action) {
    switch (action) {
      case 'highlight_product':
        this.highlightProductImages();
        break;
      case 'show_reviews':
        this.displayReviews();
        break;
      case 'show_variants':
        this.displayVariants();
        break;
      case 'show_cta':
        this.showCallToAction();
        break;
    }
  }

  highlightProductImages() {
    const images = document.querySelectorAll('.product-image');
    images.forEach(img => {
      img.style.border = '3px solid #007bff';
      img.style.borderRadius = '10px';
    });
  }

  displayReviews() {
    const reviewsSection = document.getElementById('product-reviews');
    if (reviewsSection) {
      reviewsSection.scrollIntoView({ behavior: 'smooth' });
      reviewsSection.style.backgroundColor = '#f8f9fa';
    }
  }

  displayVariants() {
    const variantsSection = document.querySelector('.product-variants');
    if (variantsSection) {
      variantsSection.style.animation = 'pulse 1s';
    }
  }

  showCallToAction() {
    const addToCartBtn = document.querySelector('.btn-add-to-cart');
    if (addToCartBtn) {
      addToCartBtn.style.animation = 'pulse 2s infinite';
      addToCartBtn.style.backgroundColor = '#28a745';
    }
  }

  async completDemo() {
    await this.avatar.speak("That completes our product demonstration! Do you have any questions, or would you like to see other products?");
  }
}
```

### AI-Powered Recommendations

```python
# ai_recommendations.py
import json
from typing import List, Dict
import openai

class AIProductRecommendation:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        
    async def get_personalized_recommendations(self, 
                                            customer_data: dict, 
                                            product_catalog: List[dict],
                                            interaction_history: List[dict]) -> List[dict]:
        """Generate AI-powered product recommendations"""
        
        # Prepare context for AI
        context = self.prepare_recommendation_context(
            customer_data, 
            product_catalog, 
            interaction_history
        )
        
        # Query OpenAI for recommendations
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.get_recommendation_prompt()},
                {"role": "user", "content": context}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Parse recommendations
        recommendations = self.parse_ai_response(response.choices[0].message.content)
        
        return recommendations
    
    def prepare_recommendation_context(self, customer_data, products, history):
        """Prepare context for AI recommendation"""
        context = {
            "customer": {
                "previous_purchases": customer_data.get('orders', []),
                "browsing_history": customer_data.get('viewed_products', []),
                "preferences": customer_data.get('preferences', {})
            },
            "available_products": products[:20],  # Limit for token efficiency
            "recent_interactions": history[-10:]  # Last 10 interactions
        }
        
        return json.dumps(context, indent=2)
    
    def get_recommendation_prompt(self):
        """Get the AI prompt for recommendations"""
        return """You are an expert sales assistant for an e-commerce store. 
        Based on the customer data and available products, recommend 3-5 products that would be most relevant and appealing to this customer.
        
        Consider:
        - Customer's purchase history and preferences
        - Current browsing behavior
        - Product popularity and ratings
        - Complementary product relationships
        - Seasonal relevance
        
        Respond with a JSON array of recommendations, each containing:
        - product_id
        - reason (why this product fits the customer)
        - confidence_score (1-10)
        
        Format your response as valid JSON only."""
    
    def parse_ai_response(self, response_text: str) -> List[dict]:
        """Parse AI response into structured recommendations"""
        try:
            recommendations = json.loads(response_text)
            return recommendations
        except json.JSONDecodeError:
            # Fallback to manual parsing if JSON is malformed
            return self.extract_recommendations_fallback(response_text)
    
    def extract_recommendations_fallback(self, text: str) -> List[dict]:
        """Fallback recommendation extraction"""
        # Simple extraction logic for malformed JSON
        return []

# Integration with Shopify avatar
class SmartShopifyAvatar:
    def __init__(self):
        self.ai_recommendations = AIProductRecommendation(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
    async def handle_smart_recommendation_request(self, context: dict):
        """Handle AI-powered recommendation requests"""
        customer_data = context.get('customer', {})
        
        # Get product catalog
        products = await self.get_product_catalog()
        
        # Get interaction history
        history = await self.get_interaction_history(customer_data.get('id'))
        
        # Generate AI recommendations
        recommendations = await self.ai_recommendations.get_personalized_recommendations(
            customer_data, products, history
        )
        
        # Format response for avatar
        response_text = self.format_recommendation_response(recommendations)
        
        return {
            'text': response_text,
            'actions': [
                {
                    'type': 'show_recommendations',
                    'products': [self.get_product_by_id(r['product_id']) for r in recommendations]
                }
            ]
        }
    
    def format_recommendation_response(self, recommendations: List[dict]) -> str:
        """Format AI recommendations into natural speech"""
        if not recommendations:
            return "I'd be happy to show you some of our featured products that I think you'd love!"
        
        intro = "Based on your interests and shopping history, I have some perfect recommendations for you! "
        
        product_mentions = []
        for rec in recommendations[:3]:  # Mention top 3
            product = self.get_product_by_id(rec['product_id'])
            reason = rec.get('reason', 'it\'s very popular')
            product_mentions.append(f"our {product['title']} because {reason}")
        
        return intro + "I especially recommend " + ", and ".join(product_mentions) + ". Would you like to see these products?"
```

## Performance Optimization

### Caching Strategy

```python
# shopify_cache.py
import redis
import json
from datetime import timedelta

class ShopifyCacheManager:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = timedelta(hours=1)
        
    async def cache_product(self, product_id: str, product_data: dict):
        """Cache product data"""
        cache_key = f"product:{product_id}"
        await self.redis_client.setex(
            cache_key,
            self.default_ttl,
            json.dumps(product_data)
        )
    
    async def get_cached_product(self, product_id: str) -> dict:
        """Get cached product data"""
        cache_key = f"product:{product_id}"
        cached_data = await self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def cache_customer_profile(self, customer_id: str, profile_data: dict):
        """Cache customer profile and preferences"""
        cache_key = f"customer_profile:{customer_id}"
        await self.redis_client.setex(
            cache_key,
            timedelta(hours=24),  # Longer TTL for customer data
            json.dumps(profile_data)
        )
    
    async def invalidate_product_cache(self, product_id: str):
        """Invalidate product cache when updated"""
        cache_key = f"product:{product_id}"
        await self.redis_client.delete(cache_key)
```

## Analytics and Insights

### Conversation Analytics

```python
# analytics.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

@dataclass
class ConversationMetrics:
    session_id: str
    customer_id: str
    start_time: datetime
    end_time: datetime
    message_count: int
    products_discussed: List[str]
    conversion_events: List[dict]
    sentiment_score: float
    satisfaction_rating: int = None

class ShopifyAvatarAnalytics:
    def __init__(self):
        self.sessions: Dict[str, ConversationMetrics] = {}
        
    def start_session(self, session_id: str, customer_id: str):
        """Start tracking a new conversation session"""
        self.sessions[session_id] = ConversationMetrics(
            session_id=session_id,
            customer_id=customer_id,
            start_time=datetime.now(),
            end_time=None,
            message_count=0,
            products_discussed=[],
            conversion_events=[],
            sentiment_score=0.0
        )
    
    def track_message(self, session_id: str, message: str, sender: str):
        """Track individual messages"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.message_count += 1
            
            # Analyze sentiment
            if sender == 'customer':
                sentiment = self.analyze_sentiment(message)
                session.sentiment_score = (session.sentiment_score + sentiment) / 2
    
    def track_product_discussion(self, session_id: str, product_id: str):
        """Track when products are discussed"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if product_id not in session.products_discussed:
                session.products_discussed.append(product_id)
    
    def track_conversion_event(self, session_id: str, event_type: str, data: dict):
        """Track conversion events (add to cart, purchase, etc.)"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.conversion_events.append({
                'type': event_type,
                'timestamp': datetime.now(),
                'data': data
            })
    
    def end_session(self, session_id: str, satisfaction_rating: int = None):
        """End conversation session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.end_time = datetime.now()
            session.satisfaction_rating = satisfaction_rating
    
    def analyze_sentiment(self, message: str) -> float:
        """Simple sentiment analysis (replace with proper NLP)"""
        positive_words = ['good', 'great', 'love', 'excellent', 'perfect', 'amazing']
        negative_words = ['bad', 'hate', 'terrible', 'awful', 'horrible', 'worst']
        
        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count == negative_count:
            return 0.0
        elif positive_count > negative_count:
            return min(1.0, positive_count * 0.3)
        else:
            return max(-1.0, negative_count * -0.3)
    
    def generate_insights(self) -> Dict:
        """Generate analytics insights"""
        if not self.sessions:
            return {}
        
        sessions = list(self.sessions.values())
        completed_sessions = [s for s in sessions if s.end_time]
        
        if not completed_sessions:
            return {'error': 'No completed sessions'}
        
        # Calculate metrics
        avg_session_duration = sum(
            (s.end_time - s.start_time).total_seconds() 
            for s in completed_sessions
        ) / len(completed_sessions)
        
        avg_message_count = sum(s.message_count for s in completed_sessions) / len(completed_sessions)
        
        conversion_rate = len([
            s for s in completed_sessions 
            if any(e['type'] == 'purchase' for e in s.conversion_events)
        ]) / len(completed_sessions)
        
        avg_sentiment = sum(s.sentiment_score for s in completed_sessions) / len(completed_sessions)
        
        return {
            'total_sessions': len(completed_sessions),
            'avg_session_duration_seconds': avg_session_duration,
            'avg_messages_per_session': avg_message_count,
            'conversion_rate': conversion_rate,
            'avg_sentiment_score': avg_sentiment,
            'most_discussed_products': self.get_most_discussed_products(),
            'satisfaction_scores': [
                s.satisfaction_rating for s in completed_sessions 
                if s.satisfaction_rating is not None
            ]
        }
    
    def get_most_discussed_products(self) -> List[tuple]:
        """Get most frequently discussed products"""
        product_counts = {}
        for session in self.sessions.values():
            for product_id in session.products_discussed:
                product_counts[product_id] = product_counts.get(product_id, 0) + 1
        
        return sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10]
```

## Best Practices

### 1. User Experience
- Keep avatar responses concise and helpful
- Provide clear navigation options
- Implement fallback responses for unrecognized queries
- Ensure fast response times (<3 seconds)

### 2. Product Knowledge
- Maintain up-to-date product information
- Include accurate pricing and availability
- Provide detailed size guides and specifications
- Handle product variations correctly

### 3. Privacy & Security
- Follow Shopify's privacy guidelines
- Secure customer data transmission
- Implement proper authentication
- Respect customer consent preferences

### 4. Performance
- Cache frequently accessed data
- Optimize avatar loading times
- Implement proper error handling
- Monitor conversation quality

## Troubleshooting

### Common Issues

#### Integration Setup
```javascript
// Debug API connections
async function debugShopifyIntegration() {
  try {
    // Test Shopify API
    const products = await fetch('/admin/api/2023-10/products.json');
    console.log('Shopify API:', products.ok ? 'Connected' : 'Failed');
    
    // Test bitHuman API
    const avatar = await BitHumanAvatar.test();
    console.log('bitHuman API:', avatar ? 'Connected' : 'Failed');
    
  } catch (error) {
    console.error('Integration test failed:', error);
  }
}
```

#### Performance Issues
```python
# Monitor avatar response times
import time

async def monitor_response_time(message_handler):
    start_time = time.time()
    response = await message_handler.process_message(message)
    response_time = time.time() - start_time
    
    if response_time > 3.0:
        print(f"Slow response: {response_time:.2f}s")
        # Log for optimization
    
    return response
```

## Next Steps

To enhance your Shopify integration:

1. **[Explore Other Integrations](livekit.md)** - Add video conferencing features
2. **[Review Examples](../examples/voice-driven-audio.md)** - See complete implementations
3. **[Optimize Performance](../build/gpu-cloud.md)** - Use GPU cloud for better response times
4. **[Deploy at Scale](../build/self-hosted.md)** - Handle high-traffic stores

## Resources

- **[Shopify Partner Documentation](https://shopify.dev/)** - Complete Shopify development guides
- **[Shopify App Store](https://apps.shopify.com/)** - Browse existing apps for inspiration
- **[Liquid Template Language](https://shopify.github.io/liquid/)** - Shopify's templating system
- **[Community Examples](https://console.bithuman.io/#community)** - See other e-commerce integrations

Transform your Shopify store with intelligent avatar assistants that provide personalized, engaging customer experiences! 