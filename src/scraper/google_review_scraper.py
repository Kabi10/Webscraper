import googlemaps
from typing import List, Dict
import asyncio

class GoogleReviewScraper:
    def __init__(self, api_key: str):
        self.client = googlemaps.Client(key=api_key)
        self.location = {
            'lat': 49.2163,  # Pitt Meadows coordinates
            'lng': -122.6894
        }
        self.search_radius = 15000  # 15km radius to cover both Pitt Meadows and nearby areas
        
    def filter_employment_keywords(self, text: str) -> bool:
        """Enhanced employment keyword detection"""
        keywords = {
            # Direct employment terms (highest weight)
            'workplace': 3,
            'worked here': 3,
            'working here': 3,
            'employee': 3,
            'employer': 3,
            'employed': 3,
            'salary': 3,
            'wage': 3,
            'wages': 3,
            
            # Industry specific terms (high weight)
            'cultivation': 2.5,
            'growing': 2.5,
            'processing': 2.5,
            'packaging': 2.5,
            'production': 2.5,
            'quality control': 2.5,
            'compliance': 2.5,
            'facility': 2.5,
            
            # Work environment terms (medium-high weight)
            'management': 2,
            'supervisor': 2,
            'manager': 2,
            'benefits': 2,
            'work-life': 2,
            'work life': 2,
            'shifts': 2,
            'coworkers': 2,
            'co-workers': 2,
            
            # General work terms (medium weight)
            'job': 1.5,
            'pay': 1.5,
            'staff': 1.5,
            'team': 1.5,
            'hours': 1.5,
            'schedule': 1.5,
            'position': 1.5,
            
            # Culture and environment (standard weight)
            'toxic': 1,
            'culture': 1,
            'environment': 1,
            'training': 1,
            'experience': 1,
            'safety': 1,
            'clean': 1
        }
        
        text = text.lower()
        score = sum(weight for keyword, weight in keywords.items() 
                   if keyword in text)
        return score >= 1.0  # Lower threshold to catch more reviews

    async def get_delta_bc_reviews(self, business_type: str = None, max_results: int = 10) -> List[Dict]:
        """Fetch employment-related reviews specifically for Delta, BC businesses"""
        try:
            # Search for places in Delta, BC
            places_result = self.client.places_nearby(
                location=self.location,
                radius=self.search_radius,
                keyword=business_type
            )
            
            if not places_result.get('results'):
                print(f"📍 No places found matching '{business_type}' in Delta, BC")
                return []
            
            print(f"📍 Found {len(places_result['results'])} places to check...")
            
            reviews = []
            results_count = 0
            
            # Process each place
            for place in places_result['results'][:5]:
                if results_count >= max_results:
                    break
                
                business_name = place.get('name', 'Unknown Business')
                print(f"🏢 Checking: {business_name}")
                
                try:
                    # Try text search first
                    search_result = self.client.places(
                        query=f"{business_name} Delta BC",
                        location=self.location,
                        radius=5000
                    )
                    
                    if search_result.get('results'):
                        place_id = search_result['results'][0]['place_id']
                        
                        # Get place details
                        place_details = self.client.place(
                            place_id,
                            fields=['name', 'formatted_address', 'rating', 'reviews', 'user_ratings_total']
                        )
                        
                        if place_details.get('reviews'):
                            print(f"📝 Found {len(place_details['reviews'])} reviews")
                            
                            for review in place_details['reviews']:
                                if self.filter_employment_keywords(review['text']):
                                    reviews.append({
                                        'business_name': place_details['name'],
                                        'address': place_details.get('formatted_address', 'Address not available'),
                                        'text': review['text'],
                                        'rating': review['rating'],
                                        'time': review['relative_time_description'],
                                        'author': review['author_name'],
                                        'employment_related': True
                                    })
                                    results_count += 1
                                    print(f"✨ Found employment-related review!")
                                    
                                    if results_count >= max_results:
                                        break
                        else:
                            print(f"ℹ️ No reviews available")
                    
                except Exception as place_error:
                    print(f"⚠️ Error checking {business_name}: {str(place_error)}")
                    continue
                
                await asyncio.sleep(2)  # Conservative rate limiting
            
            return reviews
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []
    
    # Keep the original get_reviews method as fallback
    async def get_reviews(self, company_name: str) -> List[Dict]:
        """Fetch and filter employment-related reviews"""
        try:
            # Use text search for more accurate results
            search_result = self.client.places(
                query=company_name,
                location=self.location,
                radius=10000,
                type='establishment'
            )
            
            if not search_result.get('results'):
                print(f"📍 No places found matching: {company_name}")
                return []
            
            # Get the most relevant result
            place = search_result['results'][0]
            print(f"🏢 Found: {place.get('name', 'Unknown')} ({place.get('formatted_address', 'No address')})")
            
            # Get place details with reviews
            place_details = self.client.place(
                place['place_id'],
                fields=['name', 'formatted_address', 'rating', 'reviews', 'user_ratings_total']
            )
            
            if not place_details.get('reviews'):
                print(f"ℹ️ No reviews available")
                return []
            
            print(f"\n📝 Found {len(place_details['reviews'])} total reviews:")
            reviews = []
            
            # Print all reviews for inspection
            for i, review in enumerate(place_details['reviews'], 1):
                print(f"\n--- Review {i} ---")
                print(f"Author: {review['author_name']}")
                print(f"Rating: {review['rating']} stars")
                print(f"Time: {review['relative_time_description']}")
                print(f"Text: {review['text']}")
                print("-" * 80)
                
                # Check if employment related
                if (
                    self.filter_employment_keywords(review['text']) or
                    "work" in review['text'].lower() or
                    "employee" in review['text'].lower() or
                    "manager" in review['text'].lower() or
                    any(phrase in review['text'].lower() for phrase in [
                        "place to work",
                        "working here",
                        "worked here",
                        "workplace",
                        "management",
                        "staff"
                    ])
                ):
                    reviews.append({
                        'text': review['text'],
                        'rating': review['rating'],
                        'time': review['relative_time_description'],
                        'author': review['author_name'],
                        'employment_related': True
                    })
                    print(f"✨ This review appears to be employment-related!")
            
            return reviews
            
        except Exception as e:
            if "API key is expired" in str(e):
                print("⚠️ API Key Issue: Please check if Places API is enabled and the key is active")
            else:
                print(f"❌ Error: {str(e)}")
            return [] 