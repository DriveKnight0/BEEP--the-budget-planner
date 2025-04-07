import json
import re
import random
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai
from web_search import get_financial_advice

# Load environment variables
load_dotenv()

class SmartBudgetAIChatbot:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key not found in environment variables")
            
        print("Initializing SmartBudget AI with Gemini...")
        genai.configure(api_key=api_key)
        
        # Initialize Gemini model with safety settings
        try:
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            self.chat = self.model.start_chat(history=[])
            print("Gemini model initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini API: {str(e)}")
            print("Falling back to local implementation")
            self.model = None
            self.chat = None
        
        self.user_data = {}
        self.expenses = {}
        self.conversation_history = []
        self.user_name = None
        self.capabilities = [
            "Create and manage monthly budgets 💰",
            "Plan and optimize travel budgets ✈️",
            "Track travel expenses and savings 🎒",
            "Set travel savings goals 🎯",
            "Analyze spending patterns for travel 📈",
            "Calculate travel expense ratios 📊",
            "Suggest travel cost-saving strategies 💡",
            "Help with travel budget management 📉",
            "Provide up-to-date FD rates from major banks 🏦",
            "Compare various banking products and services 💳",
            "Offer information about loan interest rates 🏠",
            "Explain different types of bank accounts and their benefits 💼"
        ]
        self.last_greeting_time = None
        
        # Financial advice templates - kept for fallback mode
        self.advice_templates = [
            "Based on your expenses, you might want to consider reducing your {category} spending by {percent}% to save more money.",
            "I notice that you're spending {amount} on {category}. That's about {percent}% of your income. The recommended percentage is around {recommended}%.",
            "Looking at your financial data, I suggest focusing on saving more in the {category} category. Try to aim for {goal} per month.",
            "Your {category} expenses seem {status}. Most financial experts recommend keeping it under {recommended}% of your income.",
            "To reach your savings goal of {savings_goal}, consider cutting back on {category} by about {amount} per month.",
            "Great job on managing your {category}! You're spending less than the recommended amount.",
            "To improve your financial health, try the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings.",
            "Looking at your spending, I recommend creating an emergency fund of at least 3-6 months of expenses.",
            "Consider automating your savings by setting up automatic transfers to your savings account each month."
        ]
        
        # Response templates - kept for fallback mode
        self.response_templates = {
            "greeting": [
                "👋 Hello {name}! How can I help with your finances today?",
                "Hi there, {name}! Ready to talk about your budget and savings?",
                "Hello {name}! I'm here to help you manage your money better. What can I do for you today?",
                "Hey {name}! Your financial assistant is ready to help. What would you like to do today?"
            ],
            "income_added": [
                "✅ Great! I've recorded your monthly income as ₹{income}.",
                "Thanks! I've noted your income as ₹{income} per month."
            ],
            "expense_added": [
                "📝 Got it! I've added ₹{amount} for {category} to your expenses.",
                "Added: ₹{amount} for {category}. Your total expenses are now ₹{total_expenses}."
            ],
            "savings_goal_added": [
                "🎯 Excellent! Your savings goal is set to ₹{goal} per month.",
                "I've set your monthly savings goal to ₹{goal}. Let's work towards achieving it!"
            ],
            "budget_analysis": [
                "📊 Based on your information:\n• Income: ₹{income}\n• Total Expenses: ₹{total_expenses}\n• Remaining: ₹{remaining}\n\n{advice}",
                "💰 Here's your financial snapshot:\n• Monthly Income: ₹{income}\n• Total Expenses: ₹{total_expenses}\n• Available for Savings: ₹{remaining}\n\n{advice}"
            ],
            "general": [
                "I'm here to help with your budget! You can tell me about your income, expenses, or savings goals.",
                "Need help with something specific? You can ask me about budget analysis, expense tracking, or savings advice.",
                "Feel free to share more details about your financial situation so I can provide better advice.",
                "Is there anything specific about your finances you'd like to discuss today?"
            ]
        }

    def get_ai_response(self, user_input):
        if not self.model or not self.chat:
            return self.generate_fallback_response(user_input)
            
        try:
            # Process user input for financial information
            self.extract_financial_info(user_input)
            
            # Prepare context for the AI
            context = self.format_conversation_history()
            financial_context = self.format_financial_context()
            
            # Create a focused prompt for the AI
            prompt = f"""You are BEEP (Budgeting & Expense Estimation Planner), a fun but focused financial buddy! 🎯

Core Mission: Help users achieve their financial goals through friendly guidance and practical advice.

Style & Focus Guide:
- Stay 100% focused on financial topics - politely redirect any off-topic questions
- Be fun and friendly, but always bring it back to financial goals
- Use emojis to make finance fun (2-3 per message)
- Keep responses focused on actionable financial advice
- Always ask about or reference specific financial goals
- If user asks non-financial questions, gently redirect to:
  * Budgeting
  * Saving
  * Investing
  * Expense tracking
  * Financial planning

Previous chat:
{context}

Their financial info:
{financial_context}

Key Behaviors:
1. Always ask about or reference their financial goals 🎯
2. Give specific, actionable money advice 💡
3. Use simple language but stay professional 📊
4. Be encouraging about financial progress 🌟
5. Redirect non-financial topics back to money goals

Remember: You're their financial success coach! Keep them focused on their money goals.

Their message: {user_input}"""

            # Get response from Gemini
            response = self.chat.send_message(prompt)
            
            # Make sure we have emojis in fallback responses too
            if not response.text:
                return self.generate_fallback_response(user_input)

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response.text})

            return response.text
            
        except Exception as e:
            print(f"Error getting Gemini response: {str(e)}")
            return self.generate_fallback_response(user_input)

    def generate_fallback_response(self, user_input):
        """Generate a goal-oriented response when AI is unavailable"""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['hi', 'hello', 'hey']):
            return "Hey there! 👋 I'm BEEP, your financial goals coach! 🎯 Let's work on achieving your money goals together! What financial target would you like to hit first? 💪"
            
        if 'budget' in input_lower:
            return "Perfect focus on budgeting! 🎯 A solid budget is key to reaching your financial goals. What specific money target are you aiming for? Let's build a plan to get you there! 📊"
            
        if any(word in input_lower for word in ['save', 'saving', 'savings']):
            return "Love your focus on saving! 🎯 Setting clear savings goals is crucial for financial success. What's your target savings amount? Let's create a strategy to achieve it! 💰"
            
        if any(word in input_lower for word in ['invest', 'investment']):
            return "Smart thinking about investing! 🎯 What's your investment goal - retirement, buying a house, or something else? Let's build an investment strategy to match your targets! 📈"
            
        if any(word in input_lower for word in ['expense', 'spending']):
            return "Great focus on expenses! 🔍 Understanding your spending is key to reaching financial goals. What's your target budget? Let's track those expenses and align them with your objectives! 🎯"
            
        # Default response if no patterns match
        return "Let's focus on your financial success! 🎯 What's your biggest money goal right now? Whether it's saving, investing, or budgeting, I'm here to help you create a solid plan to achieve it! 💪"

    def extract_financial_info(self, user_input):
        """Extract financial information from user input"""
        # Extract amounts
        amount_pattern = r'(?:₹|Rs\.?|INR)\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        amounts = re.findall(amount_pattern, user_input)
        
        # Extract expense categories
        expense_categories = ['food', 'rent', 'transport', 'utilities', 'entertainment', 'shopping']
        found_categories = [cat for cat in expense_categories if cat in user_input.lower()]
        
        # Update user data if relevant information is found
        if amounts and found_categories:
            amount = float(amounts[0].replace(',', ''))
            category = found_categories[0]
            if category not in self.expenses:
                self.expenses[category] = []
            self.expenses[category].append(amount)

    def format_conversation_history(self):
        """Format conversation history for context"""
        if not self.conversation_history:
            return "No previous conversation."
        
        formatted_history = []
        for msg in self.conversation_history[-5:]:  # Only use last 5 messages for context
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted_history.append(f"{role}: {content}")
            
        return "\n".join(formatted_history)

    def format_financial_context(self):
        """Format current financial context"""
        if not self.expenses:
            return "No financial information provided yet."
            
        context = ["Current financial information:"]
        for category, amounts in self.expenses.items():
            total = sum(amounts)
            context.append(f"- {category.capitalize()}: ₹{total:,.2f}")
            
        return "\n".join(context)

    def handle_greeting(self, user_input):
        greetings = ['hi', 'hello', 'hey', 'hola', 'greetings']
        current_time = datetime.now()
        if any(greeting in user_input.lower() for greeting in greetings):
            if self.last_greeting_time is None or (current_time - self.last_greeting_time).seconds > 300:
                self.last_greeting_time = current_time
                responses = [
                    "👋 Hi there! I'm your AI financial buddy. Want to know what I can do? Just ask 'what can you do?' Or we can start budgeting - what's your name?",
                    "Hello! I'm here to help with your finances. Ask me 'what can you do?' to learn more, or we can get started - what's your name?",
                    "Hey! 😊 I'm your personal finance assistant. Want to see my capabilities? Ask 'what can you do?' Or let's begin - what's your name?",
                    "Hi! Ready to manage your finances better? Ask me 'what can you do?' to learn more, or we can start right away - what's your name?"
                ]
                return random.choice(responses)
            return "I'm here to help! Just let me know what you need."
        return None

    def handle_capabilities(self, user_input):
        capability_pattern = r'(?i)(?:what can you do|capabilities|features|help me with|what do you do|how can you help)'
        capability_match = re.search(capability_pattern, user_input)
        
        if capability_match:
            response = "💡 I can help you with:\n\n"
            
            # Group capabilities by category for better organization
            budget_capabilities = [cap for cap in self.capabilities[:4]]
            travel_capabilities = [cap for cap in self.capabilities[4:8]]
            banking_capabilities = [cap for cap in self.capabilities[8:]]
            
            response += "📒 Budget Management:\n"
            response += "\n".join(budget_capabilities)
            
            response += "\n\n✈️ Travel Finance:\n"
            response += "\n".join(travel_capabilities)
            
            response += "\n\n🏦 Banking Information:\n"
            response += "\n".join(banking_capabilities)
            
            response += "\n\nWhat would you like help with today?"
            return response
            
        return None

    def get_greeting(self):
        greetings = [
            "Hey there! 👋 I'm your personal finance buddy. What's your name?",
            "Hi! I'm excited to help you manage your finances better. What should I call you?",
            "Welcome! I'm your AI financial assistant. Before we start, could you tell me your name?",
            "Hello! Let's work on your budget together. First, what's your name?"
        ]
        return random.choice(greetings)

    def get_income_question(self):
        questions = [
            f"Thanks {self.user_name}! Let's start with your monthly income - how much do you earn?",
            f"Great to meet you, {self.user_name}! To help you better, could you tell me your monthly income?",
            f"Alright {self.user_name}! What's your monthly income? This will help me understand your financial situation.",
            f"Perfect, {self.user_name}! How much money do you make each month?"
        ]
        return random.choice(questions)

    def get_expense_prompt(self):
        prompts = [
            f"Now {self.user_name}, tell me about your expenses. You can add any category you want! For example, say something like 'I spend 5000 on groceries' or '3000 for gaming'.",
            f"Let's talk about where your money goes, {self.user_name}. Just tell me naturally about any expense category - could be anything from 'coffee' to 'pet care'!",
            f"What kind of things do you spend money on, {self.user_name}? You can tell me about any category - like '2000 on movies' or '6000 for hobbies'.",
            f"Time to track your spending, {self.user_name}! Share your expenses in any categories you like - maybe start with your biggest expense?"
        ]
        return random.choice(prompts)

    def get_expense_acknowledgment(self, category, amount):
        acks = [
            f"Got it! ₹{amount:,.2f} for {category}. What other expenses would you like to add?",
            f"Added ₹{amount:,.2f} for {category}. Tell me about another expense, or say 'done' when you're finished!",
            f"Noted ₹{amount:,.2f} for {category}. What else do you spend money on?",
            f"I've recorded ₹{amount:,.2f} for {category}. Keep going! Or say 'done' if that's all."
        ]
        return random.choice(acks)

    def get_savings_question(self):
        questions = [
            f"Great job listing your expenses, {self.user_name}! How much would you like to save each month?",
            f"Now let's set a savings target, {self.user_name}. How much would you like to set aside monthly?",
            f"Time to think about savings, {self.user_name}! What's your monthly savings goal?",
            f"Let's plan your savings, {self.user_name}. How much do you want to save each month?"
        ]
        return random.choice(questions)

    def extract_number(self, text):
        numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', text)
        if numbers:
            return float(numbers[0].replace(',', ''))
        return None

    def extract_category(self, text):
        # Remove common expense-related words and amounts
        text = re.sub(r'\d+(?:,\d+)*(?:\.\d+)?', '', text)
        text = text.lower()
        words_to_remove = ['spend', 'spent', 'spending', 'pay', 'paid', 'paying', 'cost', 'costs', 'costing',
                          'rupees', 'rs', 'inr', '₹', 'on', 'for', 'in', 'my', 'i', 'around', 'about']
        
        for word in words_to_remove:
            text = text.replace(word, '')
        
        # Clean up the remaining text
        category = text.strip()
        if category:
            # Take the last meaningful word/phrase as the category
            category_parts = [part for part in category.split() if len(part) > 1]
            if category_parts:
                return ' '.join(category_parts)
        return None

    def process_input(self, user_input):
        # Extract name if not set
        if not self.user_name:
            name_match = re.search(r'my name is (\w+)', user_input.lower())
            if name_match:
                self.user_name = name_match.group(1).title()

        # Get AI response
        return self.get_ai_response(user_input)

    def get_bank_information(self, query_type):
        """
        Get real-time bank information using web search.
        
        Args:
            query_type (str): Type of bank information to retrieve (fd_rates, savings, loans, etc.)
        
        Returns:
            str: Formatted information about bank products and rates
        """
        try:
            # Construct appropriate search query based on query type
            if 'fd' in query_type.lower() or 'fixed deposit' in query_type.lower():
                search_query = "latest FD interest rates comparison major banks India"
            elif 'saving' in query_type.lower():
                search_query = "best savings account interest rates India comparison"
            elif 'loan' in query_type.lower():
                search_query = "current loan interest rates comparison banks India"
            elif 'credit card' in query_type.lower():
                search_query = "best credit card offers India comparison"
            else:
                search_query = f"latest {query_type} banking products India comparison"
                
            # Use web_search to get information
            bank_info = get_financial_advice(search_query)
            
            # Construct a user-friendly response
            response = f"📊 Latest {query_type.title()} Information:\n\n"
            response += bank_info
            
            # Add a disclaimer
            response += "\n\n⚠️ Note: Rates may vary. Please check with banks for the most current information."
            
            return response
        except Exception as e:
            # Fallback response if web search fails
            return f"""Sorry, I couldn't get the latest information on {query_type}. Here's what I know:
            
• Fixed deposit rates typically range from 3-7% depending on the bank and duration
• Senior citizens usually get 0.25-0.5% higher rates
• Most banks offer higher rates for longer duration deposits
• Special FD schemes may have higher rates but limited periods
• Some banks offer additional benefits for existing customers

Please check with specific banks for their current rates and offers."""
