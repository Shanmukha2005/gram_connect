# Gram Connect - AI Shopping Assistant

## Overview
Gram Connect is a comprehensive e-commerce platform that connects shopkeepers, customers, and delivery partners. The platform now features an intelligent AI shopping assistant that helps users with various shopping-related queries.

## Features

### 🤖 AI Shopping Assistant
The platform includes a sophisticated AI chatbot that provides intelligent responses to user queries about:

- **Order Management**: Track orders, check delivery status, and manage order history
- **Product Information**: Find products, browse categories, and get product details
- **Payment & Security**: Information about payment methods, security, and transaction safety
- **Returns & Refunds**: Return policies, refund processes, and exchange information
- **Shop Verification**: Details about trusted shops, verification processes, and ratings
- **Delivery Options**: Multiple delivery methods, timing, and location-based services
- **Customer Support**: 24/7 assistance, contact information, and self-service options

### 🎯 Quick Tips
The AI bot features quick tip buttons for common questions:
- Track Order
- Payment Methods
- Returns Process
- Delivery Options
- Shop Trust
- Deals & Discounts

### 💬 Intelligent Conversations
The AI bot understands context and provides personalized responses based on:
- User query keywords
- Question complexity
- E-commerce domain knowledge
- Platform-specific information

## Technical Implementation

### Backend
- **Django Views**: RESTful API endpoints for AI chat functionality
- **Response Generation**: Context-aware response system with keyword matching
- **CSRF Protection**: Secure communication with proper token handling

### Frontend
- **Modern UI**: Beautiful gradient design with smooth animations
- **Responsive Design**: Works seamlessly on all device sizes
- **Real-time Chat**: Typing indicators and smooth message flow
- **CSS Classes**: Clean, maintainable styling with hover effects

### API Endpoints
- `POST /api/ai/chat/`: Main AI chat endpoint
- `POST /api/customer/login/`: Customer authentication
- `POST /api/customer/register/`: Customer registration
- `GET /api/products/`: Product browsing and search

## Usage

### For Customers
1. Click the floating AI bot icon (🤖) on any page
2. Ask questions about products, orders, payments, or services
3. Use quick tip buttons for common questions
4. Get instant, helpful responses from the AI assistant

### For Developers
The AI bot can be extended by:
- Adding new response patterns in `generate_ai_response()`
- Creating additional quick tip categories
- Integrating with external AI services
- Adding conversation memory and context

## Installation & Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Start the server: `python manage.py runserver`
5. Access the AI bot on any page

## Future Enhancements

- **Machine Learning Integration**: Connect with external AI models for more sophisticated responses
- **Conversation Memory**: Remember user preferences and conversation history
- **Multi-language Support**: Support for multiple languages
- **Voice Integration**: Voice-to-text and text-to-speech capabilities
- **Product Recommendations**: AI-powered product suggestions based on user queries

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License.
