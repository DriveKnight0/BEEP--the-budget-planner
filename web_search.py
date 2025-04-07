def clean_and_format_advice(search_results):
    # Extract relevant information and format it as bullet points
    advice_points = []
    
    for result in search_results:
        # Clean and format the text
        text = result.get('snippet', '').strip()
        if text and len(text) > 30:  # Ensure meaningful content
            # Remove any unwanted characters and format
            text = text.replace('...', '').strip()
            if not text.startswith('•'):
                text = '• ' + text
            advice_points.append(text)
    
    # Return unique advice points
    unique_points = list(dict.fromkeys(advice_points))
    return '\n'.join(unique_points[:5])  # Return top 5 unique points

def get_financial_advice(query):
    try:
        # Try to use web_search tool if available
        try:
            from cursor_tools import web_search
            results = web_search(
                search_term=query,
                explanation="Searching for financial advice and recommendations"
            )
            
            if results and isinstance(results, list):
                return clean_and_format_advice(results)
        except ImportError:
            # cursor_tools not available in deployment environment
            pass
            
        # Fallback to static advice
        return get_fallback_advice(query)
    except Exception as e:
        return get_fallback_advice(query)

def get_fallback_advice(query):
    # Provide relevant fallback advice based on the query type
    if 'savings' in query.lower():
        return """• Create a detailed monthly budget and track all expenses
• Use automatic transfers to your savings account
• Look for ways to reduce recurring bills
• Consider a side hustle for additional income
• Use the 50/30/20 budgeting rule"""
    elif 'investment' in query.lower():
        return """• Consider mutual funds for long-term wealth creation
• Explore fixed deposits for stable returns
• Look into government savings schemes
• Diversify your investment portfolio
• Start with systematic investment plans (SIPs)"""
    elif 'expense' in query.lower():
        return """• Review and cancel unnecessary subscriptions
• Use budgeting apps to track expenses
• Look for cheaper alternatives for regular purchases
• Consider bulk buying for regular items
• Use cashback and reward programs"""
    else:
        return """• Track all income and expenses meticulously
• Set realistic financial goals
• Build an emergency fund
• Avoid unnecessary debt
• Invest in your financial education""" 