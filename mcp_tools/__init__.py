"""
MCP Tools Package
-----------------
Model Context Protocol (MCP) tools for the Agentic Supplier Risk AI system.

This package contains 4 tool groups:
1. Document Tools - PDF reading and table extraction
2. News Tools - News search and sentiment analysis
3. Registry Tools - Company verification (UK Companies House, etc.)
4. Sanctions Tools - Sanctions list checking

Each tool group is a separate module with standalone functions.
"""

__version__ = "1.0.0"
__author__ = "Agentic Supplier Risk AI Team"

# Import all tool functions for easy access
from mcp_tools.document_tools import read_pdf, extract_tables
from mcp_tools.news_tools import search_news, analyze_sentiment
from mcp_tools.registry_tools import check_uk_companies_house, verify_business_entity
from mcp_tools.sanctions_tools import check_sanctions_list, check_watchlist

__all__ = [
    # Document tools
    "read_pdf",
    "extract_tables",
    
    # News tools
    "search_news",
    "analyze_sentiment",
    
    # Registry tools
    "check_uk_companies_house",
    "verify_business_entity",
    
    # Sanctions tools
    "check_sanctions_list",
    "check_watchlist",
]