import asyncio
import os
from dotenv import load_dotenv
from scraper.google_review_scraper import GoogleReviewScraper
from config.api_config import GoogleAPIConfig

# Load environment variables
load_dotenv('.env.local')

async def test_delta_scraper():
    # Get API key from environment
    api_key = os.getenv('NEXT_PUBLIC_GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("Google Maps API key not found in .env.local")
    
    scraper = GoogleReviewScraper(api_key)
    
    # Test with manufacturing businesses first
    print("🔍 Fetching employment-related reviews in Delta, BC...")
    print("📍 Focusing on manufacturing sector...")
    
    reviews = await scraper.get_delta_bc_reviews(
        business_type="manufacturing",
        max_results=5  # Starting with a small sample
    )
    
    # Display results
    print(f"\n✨ Found {len(reviews)} employment-related reviews:")
    for i, review in enumerate(reviews, 1):
        print(f"\n📝 --- Review {i} ---")
        print(f"🏢 Business: {review['business_name']}")
        print(f"📍 Address: {review['address']}")
        print(f"⭐ Rating: {review['rating']} stars")
        print(f"🕒 Time: {review['time']}")
        print(f"💬 Review: {review['text'][:200]}..." if len(review['text']) > 200 else f"💬 Review: {review['text']}")
        print("-" * 80)

if __name__ == "__main__":
    try:
        asyncio.run(test_delta_scraper())
    except Exception as e:
        print(f"❌ Error: {str(e)}") 