"""
Agent 4: External Intelligence Agent
Role: Gather external risk signals from multiple sources
Does NOT: Make final risk decisions - only reports findings
Technology: Orchestrates MCP-2 (News), MCP-3 (Registry), MCP-4 (Sanctions)
"""

import os
import sys
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Import MCP tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tools.news_tools import search_news, analyze_sentiment
from mcp_tools.registry_tools import check_uk_companies_house, verify_business_entity
from mcp_tools.sanctions_tools import check_sanctions_list, check_watchlist

# Load environment variables
load_dotenv()


class ExternalAgent:
    """
    External Intelligence Agent - Gathers risk signals from external sources
    
    Think of this as an intelligence analyst who:
    - Searches for news articles about the supplier
    - Verifies company registration in official registries
    - Checks sanctions lists (EU, OFAC, UN)
    - Checks risk watchlists
    - Analyzes sentiment of news coverage
    - Does NOT make risk decisions - only reports findings
    """
    
    def __init__(self):
        """
        Initialize the External Intelligence Agent
        Sets up OpenAI API connection (for sentiment analysis enhancement)
        """
        # Get API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "❌ OPENAI_API_KEY not found! "
                "Make sure your .env file has: OPENAI_API_KEY=sk-..."
            )
        
        # Create OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        
        print("✅ External Intelligence Agent initialized successfully")
    
    
    def gather_intelligence(
        self,
        company_name: str,
        country: str,
        registration_number: Optional[str] = None,
        owner_names: Optional[List[str]] = None,
        search_news_enabled: bool = True,
        max_news_results: int = 5
    ) -> Dict:
        """
        Gather comprehensive external intelligence about a supplier
        
        Args:
            company_name: Name of the company to investigate
            country: Country code (e.g., "UK", "UAE", "CN")
            registration_number: Company registration number (if known)
            owner_names: List of director/owner names (for sanctions screening)
            search_news_enabled: Whether to search for news (default: True)
            max_news_results: Maximum news articles to retrieve (default: 5)
        
        Returns:
            Dictionary containing:
            - company_registry: Registration verification results
            - news_analysis: News articles and sentiment analysis
            - sanctions_check: Sanctions list screening results
            - watchlist_check: Risk watchlist screening results
            - risk_signals: Summary of red flags detected
            - data_sources: List of sources checked
        
        Example:
            result = agent.gather_intelligence(
                company_name="TechTextiles Ltd",
                country="UK",
                registration_number="12345678",
                owner_names=["John Smith"]
            )
        """
        
        print(f"\n🔍 External Intelligence Agent: Gathering intelligence on {company_name}...")
        
        intelligence = {
            "company_registry": {},
            "news_analysis": {},
            "sanctions_check": {},
            "watchlist_check": {},
            "risk_signals": [],
            "data_sources": []
        }
        
        # Step 1: Company Registry Verification
        print(f"\n   📋 Checking company registry ({country})...")
        try:
            if country.upper() == "UK" and registration_number:
                registry_result = check_uk_companies_house(registration_number)
                intelligence["company_registry"] = registry_result
                intelligence["data_sources"].append("UK Companies House")
                
                if registry_result.get("status") != "Active":
                    intelligence["risk_signals"].append(
                        f"Company status: {registry_result.get('status', 'Unknown')}"
                    )
            else:
                # Generic verification for other countries
                registry_result = verify_business_entity(company_name, country)
                intelligence["company_registry"] = registry_result
                intelligence["data_sources"].append(f"{country} Business Registry")
            
            print(f"   ✅ Registry check complete")
            
        except Exception as e:
            print(f"   ⚠️ Registry check failed: {str(e)}")
            intelligence["company_registry"] = {"error": str(e)}
        
        # Step 2: News Search and Sentiment Analysis
        if search_news_enabled:
            print(f"\n   📰 Searching news articles...")
            try:
                news_results = search_news(
                    company_name=company_name,
                    max_results=max_news_results
                )
                
                if news_results.get("articles"):
                    # Analyze sentiment of each article
                    articles_with_sentiment = []
                    positive_count = 0
                    negative_count = 0
                    neutral_count = 0
                    
                    for article in news_results["articles"]:
                        sentiment = analyze_sentiment(article.get("description", ""))
                        article["sentiment"] = sentiment
                        articles_with_sentiment.append(article)
                        
                        if sentiment == "positive":
                            positive_count += 1
                        elif sentiment == "negative":
                            negative_count += 1
                            intelligence["risk_signals"].append(
                                f"Negative news: {article.get('title', 'Unknown')}"
                            )
                        else:
                            neutral_count += 1
                    
                    intelligence["news_analysis"] = {
                        "total_articles": len(articles_with_sentiment),
                        "articles": articles_with_sentiment[:max_news_results],
                        "sentiment_summary": {
                            "positive": positive_count,
                            "negative": negative_count,
                            "neutral": neutral_count
                        },
                        "overall_sentiment": self._determine_overall_sentiment(
                            positive_count, negative_count, neutral_count
                        )
                    }
                    intelligence["data_sources"].append("NewsAPI")
                    
                    print(f"   ✅ Found {len(articles_with_sentiment)} articles")
                    print(f"      Sentiment: {positive_count} positive, {negative_count} negative, {neutral_count} neutral")
                else:
                    intelligence["news_analysis"] = {
                        "total_articles": 0,
                        "articles": [],
                        "sentiment_summary": {"positive": 0, "negative": 0, "neutral": 0},
                        "overall_sentiment": "no_coverage"
                    }
                    print(f"   ℹ️ No news articles found")
                
            except Exception as e:
                print(f"   ⚠️ News search failed: {str(e)}")
                intelligence["news_analysis"] = {"error": str(e)}
        
        # Step 3: Sanctions List Screening
        print(f"\n   🚨 Checking sanctions lists (EU, OFAC, UN)...")
        try:
            sanctions_result = check_sanctions_list(
                company_name=company_name,
                owner_names=owner_names or []
            )
            
            intelligence["sanctions_check"] = sanctions_result
            intelligence["data_sources"].extend([
                "EU Consolidated Sanctions List",
                "OFAC SDN List",
                "UN Security Council Sanctions"
            ])
            
            # Add risk signals for sanctions matches
            if sanctions_result.get("company_match", {}).get("risk_level") == "blocked":
                intelligence["risk_signals"].append(
                    f"⛔ CRITICAL: Company found on sanctions list"
                )
            elif sanctions_result.get("company_match", {}).get("risk_level") == "warning":
                intelligence["risk_signals"].append(
                    f"⚠️ WARNING: Partial match on sanctions list"
                )
            
            if sanctions_result.get("owner_matches"):
                for match in sanctions_result["owner_matches"]:
                    if match.get("risk_level") == "blocked":
                        intelligence["risk_signals"].append(
                            f"⛔ CRITICAL: Owner/Director on sanctions list: {match.get('name')}"
                        )
            
            print(f"   ✅ Sanctions check complete")
            
        except Exception as e:
            print(f"   ⚠️ Sanctions check failed: {str(e)}")
            intelligence["sanctions_check"] = {"error": str(e)}
        
        # Step 4: Risk Watchlist Screening
        print(f"\n   📊 Checking risk watchlists...")
        try:
            if registration_number:
                watchlist_result = check_watchlist(registration_number, country)
                intelligence["watchlist_check"] = watchlist_result
                intelligence["data_sources"].append("Risk Watchlists")
                
                print(f"   ✅ Watchlist check complete")
            else:
                intelligence["watchlist_check"] = {
                    "status": "skipped",
                    "reason": "No registration number provided"
                }
                print(f"   ℹ️ Watchlist check skipped (no registration number)")
                
        except Exception as e:
            print(f"   ⚠️ Watchlist check failed: {str(e)}")
            intelligence["watchlist_check"] = {"error": str(e)}
        
        # Summary
        print(f"\n✅ Intelligence gathering complete")
        print(f"   - Data sources checked: {len(intelligence['data_sources'])}")
        print(f"   - Risk signals detected: {len(intelligence['risk_signals'])}")
        
        return intelligence
    
    
    def _determine_overall_sentiment(
        self, 
        positive: int, 
        negative: int, 
        neutral: int
    ) -> str:
        """
        Determine overall sentiment from counts
        
        Returns: "mostly_positive", "mostly_negative", "mixed", or "neutral"
        """
        total = positive + negative + neutral
        
        if total == 0:
            return "no_coverage"
        
        if negative > positive + neutral:
            return "mostly_negative"
        elif positive > negative + neutral:
            return "mostly_positive"
        elif negative > 0 and positive > 0:
            return "mixed"
        else:
            return "neutral"


# Test function - MOCK VERSION (No API calls)
if __name__ == "__main__":
    """
    Test the External Intelligence Agent - MOCK VERSION
    
    This test does NOT call external APIs to save your credits.
    It only tests that the agent initializes correctly.
    
    For full testing with real external checks,
    use the workflow tests after all agents are complete.
    
    To test: python agents/external_agent.py
    """
    
    print("=" * 70)
    print("TESTING EXTERNAL INTELLIGENCE AGENT (MOCK MODE)")
    print("=" * 70)
    
    # Test 1: Agent Initialization
    print("\n🧪 TEST 1: Agent Initialization")
    print("-" * 70)
    try:
        agent = ExternalAgent()
        print("✅ Agent initialized successfully with OpenAI connection")
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        print("   Check your .env file has OPENAI_API_KEY=sk-...")
        exit(1)
    
    # Test 2: Mock Intelligence Gathering
    print("\n🧪 TEST 2: Mock External Intelligence Structure")
    print("-" * 70)
    print("   Simulating external intelligence gathering...")
    
    # Create mock intelligence result
    mock_result = {
        "company_registry": {
            "company_name": "TECHTEXTILES LIMITED",
            "company_number": "12345678",
            "status": "Active",
            "incorporation_date": "2010-03-15",
            "registered_address": "123 HIGH STREET, LONDON, E1 1AA",
            "company_type": "Private Limited Company",
            "sic_codes": ["13300 - Finishing of textiles"]
        },
        "news_analysis": {
            "total_articles": 5,
            "articles": [
                {
                    "title": "TechTextiles wins sustainability award",
                    "source": "Textile Today",
                    "date": "2025-01-15",
                    "sentiment": "positive",
                    "url": "https://example.com/article1"
                },
                {
                    "title": "UK textile exports reach record high",
                    "source": "Trade News",
                    "date": "2025-01-10",
                    "sentiment": "positive",
                    "url": "https://example.com/article2"
                },
                {
                    "title": "TechTextiles expands production capacity",
                    "source": "Business Weekly",
                    "date": "2024-12-20",
                    "sentiment": "positive",
                    "url": "https://example.com/article3"
                }
            ],
            "sentiment_summary": {
                "positive": 3,
                "negative": 0,
                "neutral": 2
            },
            "overall_sentiment": "mostly_positive"
        },
        "sanctions_check": {
            "company_match": {
                "risk_level": "clear",
                "matched": False,
                "details": "No matches found in EU, OFAC, or UN sanctions lists"
            },
            "owner_matches": [],
            "sources_checked": ["EU Consolidated List", "OFAC SDN", "UN Sanctions"]
        },
        "watchlist_check": {
            "status": "clear",
            "matched": False,
            "details": "No matches found in risk watchlists"
        },
        "risk_signals": [],
        "data_sources": [
            "UK Companies House",
            "NewsAPI",
            "EU Consolidated Sanctions List",
            "OFAC SDN List",
            "UN Security Council Sanctions",
            "Risk Watchlists"
        ]
    }
    
    # Display mock results
    print("\n" + "=" * 70)
    print("📊 MOCK EXTERNAL INTELLIGENCE RESULTS")
    print("=" * 70)
    
    print("\n📋 COMPANY REGISTRY:")
    registry = mock_result["company_registry"]
    print(f"   Name: {registry['company_name']}")
    print(f"   Number: {registry['company_number']}")
    print(f"   Status: {registry['status']}")
    print(f"   Incorporated: {registry['incorporation_date']}")
    print(f"   Type: {registry['company_type']}")
    
    print("\n📰 NEWS ANALYSIS:")
    news = mock_result["news_analysis"]
    print(f"   Total articles: {news['total_articles']}")
    print(f"   Sentiment: {news['sentiment_summary']}")
    print(f"   Overall: {news['overall_sentiment']}")
    print(f"   Sample headlines:")
    for article in news['articles'][:3]:
        print(f"      - {article['title']} ({article['sentiment']})")
    
    print("\n🚨 SANCTIONS CHECK:")
    sanctions = mock_result["sanctions_check"]
    print(f"   Company: {sanctions['company_match']['risk_level'].upper()}")
    print(f"   Owners: {len(sanctions['owner_matches'])} matches")
    print(f"   Sources: {', '.join(sanctions['sources_checked'])}")
    
    print("\n📊 WATCHLIST CHECK:")
    watchlist = mock_result["watchlist_check"]
    print(f"   Status: {watchlist['status'].upper()}")
    print(f"   Details: {watchlist['details']}")
    
    print("\n🚩 RISK SIGNALS:")
    if mock_result["risk_signals"]:
        for signal in mock_result["risk_signals"]:
            print(f"   - {signal}")
    else:
        print(f"   ✅ No risk signals detected")
    
    print(f"\n📚 DATA SOURCES CHECKED ({len(mock_result['data_sources'])}):")
    for source in mock_result["data_sources"]:
        print(f"   - {source}")
    
    print("\n" + "=" * 70)
    print("💡 NOTE: This was a MOCK test (no external API calls)")
    print("   Real external intelligence will be gathered in the full workflow.")
    print("   This includes:")
    print("   - Real UK Companies House API queries")
    print("   - Real NewsAPI searches (if API key configured)")
    print("   - Real sanctions data (276 entities, 6,403 individuals)")
    print("=" * 70)
    
    print("\n✅ EXTERNAL AGENT TESTS COMPLETED")
    print("=" * 70)