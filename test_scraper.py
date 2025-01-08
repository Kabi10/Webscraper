import asyncio
import os
import re
import csv
from datetime import datetime
from dotenv import load_dotenv
from src.scraper.google_review_scraper import GoogleReviewScraper

def highlight_employment_terms(text):
    # Employment-related terms to highlight with weights
    terms = {
        # High priority terms (weight: 8)
        'interview': 8,
        'interviewed': 8,
        'hiring': 8,
        'hired': 8,
        'fired': 8,
        'laid off': 8,
        'layoff': 8,
        'salary': 8,
        'wage': 8,
        'compensation': 8,
        
        # Work environment terms (weight: 6)
        'workplace': 6,
        'work': 6,
        'working': 6,
        'employee': 6,
        'employer': 6,
        'management': 6,
        'manager': 6,
        'supervisor': 6,
        'boss': 6,
        'hr': 6,
        'human resources': 6,
        
        # Culture terms (weight: 5)
        'culture': 5,
        'environment': 5,
        'toxic': 5,
        'benefits': 5,
        'insurance': 5,
        'vacation': 5,
        'pto': 5,
        'work-life': 5,
        
        # Role terms (weight: 4)
        'position': 4,
        'role': 4,
        'job': 4,
        'staff': 4,
        'team': 4,
        'coworker': 4,
        'colleague': 4,
        'department': 4,
        
        # General terms (weight: 3)
        'company': 3,
        'business': 3,
        'corporate': 3,
        'office': 3,
        'professional': 3,
        'career': 3,
        'training': 3
    }
    
    highlighted_text = text
    score = 0
    found_terms = []
    
    for term, weight in terms.items():
        pattern = re.compile(r'\b' + term + r'\b', re.IGNORECASE)
        if pattern.search(text):
            highlighted_text = pattern.sub(f'[{term.upper()}]', highlighted_text)
            score += weight
            found_terms.append(term)
    
    return highlighted_text, score, found_terms

def detect_position(text):
    """Enhanced position detection with more specific criteria."""
    text_lower = text.lower()
    
    # Employee indicators
    employee_terms = [
        'i work', 'worked here', 'working here', 'my job', 'my role',
        'my position', 'my manager', 'my supervisor', 'my team',
        'my department', 'my coworkers', 'my colleagues',
        'interviewed', 'got hired', 'got fired', 'laid off',
        'my salary', 'my wage', 'employee', 'employer'
    ]
    
    # Customer indicators
    customer_terms = [
        'bought', 'purchased', 'ordered', 'customer service',
        'shopping', 'shop', 'store', 'retail', 'service',
        'product quality', 'delivery', 'ordered online'
    ]
    
    # Check for employee terms first (higher priority)
    if any(term in text_lower for term in employee_terms):
        return 'Employee'
    elif any(term in text_lower for term in customer_terms):
        return 'Customer'
    
    return 'Google Reviewer'

def is_duplicate_review(review, output_file='companyreviews.csv'):
    """Check if a review already exists in the CSV file."""
    if not os.path.isfile(output_file):
        return False
        
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_reviews = list(reader)
            
            # Get the review text
            review_text = review.get('text', '')
            review_rating = review.get('rating', 0)
            
            for existing in existing_reviews:
                # Compare the content and rating
                existing_text = ''
                if existing.get('pros') and existing['pros'] != 'None provided':
                    existing_text = existing['pros']
                if existing.get('cons') and existing['cons'] != 'None provided':
                    existing_text = existing['cons']
                
                if (str(review_rating) == str(existing.get('rating', '')) and 
                    (review_text.strip() in existing_text.strip() or existing_text.strip() in review_text.strip())):
                    return True
                    
    except Exception as e:
        print(f"Warning: Error checking duplicates: {str(e)}")
        return False
        
    return False

def save_to_csv(company_name, reviews, output_file='company_reviews_new.csv'):
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(output_file)
    
    new_reviews = 0
    skipped_reviews = 0
    
    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        # Define only the required columns
        fieldnames = [
            'name',       # Company name
            'industry',   # Industry type
            'rating',     # Review rating
            'pros',       # Positive aspects
            'cons',       # Negative aspects
            'position',   # Reviewer position
            'created_at'  # Timestamp
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header only if file is new
        if not file_exists:
            writer.writeheader()
        
        # Process each review
        for review in reviews:
            # Skip if review is a duplicate
            if is_duplicate_review(review, output_file):
                skipped_reviews += 1
                continue
                
            text = review.get('text', '')
            rating = review.get('rating', 0)
            
            # Detect position from review text
            detected_position = detect_position(text)
            
            # Handle pros/cons based on rating
            if rating >= 4:  # Very positive
                pros = text
                cons = 'None provided'
            elif rating == 3:  # Neutral
                pros = text
                cons = 'None provided'
            else:  # Negative
                pros = 'None provided'
                cons = text
            
            # Create row with only required columns
            row = {
                'name': company_name,
                'industry': 'Cannabis',
                'rating': rating,
                'pros': pros,
                'cons': cons,
                'position': detected_position,
                'created_at': datetime.now().isoformat()
            }
            
            writer.writerow(row)
            new_reviews += 1
    
    print(f"\n📊 Review Statistics:")
    print(f"✨ New reviews added: {new_reviews}")
    print(f"🔄 Duplicate reviews skipped: {skipped_reviews}")

def main():
    # Load environment variables
    load_dotenv('.env.local')
    
    # Get API key
    api_key = os.getenv('NEXT_PUBLIC_GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("Google Maps API key not found in .env.local")
    
    # Debug: Print first and last 4 chars of API key
    print(f"Using API key: {api_key[:4]}...{api_key[-4:]}")
    
    # Initialize scraper
    scraper = GoogleReviewScraper(api_key)
    
    async def run_scraper():
        try:
            company_name = "BZAM Management Inc."
            company_address = "19100 Airport Way #518, Pitt Meadows, BC"
            
            # First find the place
            find_result = scraper.client.find_place(
                input=f"{company_name}, {company_address}",
                input_type="textquery",
                fields=["place_id", "name", "formatted_address", "geometry/location"]
            )
            
            if not find_result.get('candidates'):
                print("❌ Could not find the company")
                return
            
            place = find_result['candidates'][0]
            print(f"\n🏢 Found company:")
            print(f"Name: {place.get('name')}")
            print(f"Address: {place.get('formatted_address')}")
            
            # Now get place details with employment focus
            try:
                print("\n🔍 Fetching employment-related reviews...")
                details = scraper.client.place(
                    place['place_id'],
                    fields=[
                        'name',
                        'formatted_address',
                        'business_status',
                        'place_id',
                        'rating',
                        'reviews',
                        'user_ratings_total',
                        'url'
                    ],
                    language='en',
                    reviews_no_translations=True,
                    reviews_sort='newest'
                )
                
                result = details.get('result', {})
                all_reviews = []
                
                if result.get('reviews'):
                    print(f"\n📝 Found {len(result['reviews'])} total reviews")
                    # Pre-filter reviews for employment relevance
                    for review in result['reviews']:
                        text = review.get('text', '').lower()
                        # Check for employment terms (more inclusive)
                        employment_terms = [
                            # Direct employment terms
                            'work', 'employ', 'manag', 'staff',
                            'job', 'position', 'role',
                            
                            # Workplace terms
                            'office', 'place', 'company', 'business',
                            'team', 'department', 'supervisor',
                            
                            # Experience terms
                            'interview', 'hire', 'fired', 'salary',
                            'wage', 'train', 'experience',
                            
                            # Culture terms
                            'culture', 'environment', 'toxic',
                            'professional', 'standards',
                            
                            # First person indicators
                            'i work', 'worked', 'my job',
                            'my manager', 'my team', 'my role'
                        ]
                        
                        # Add review if it contains any employment term
                        if any(term in text for term in employment_terms):
                            all_reviews.append(review)
                            print(f"📌 Found employment review from {review.get('author_name', 'Anonymous')}:")
                            print(f"   {text[:100]}...")
                    
                print(f"\n📍 Place Details:")
                print(f"🏢 Name: {result.get('name')}")
                print(f"📍 Address: {result.get('formatted_address')}")
                print(f"⭐ Rating: {result.get('rating', 'N/A')}")
                print(f"📊 Total Reviews Available: {result.get('user_ratings_total', 0)}")
                print(f"📊 Employment Reviews Found: {len(all_reviews)}")
                print(f"🔗 Google Maps URL: {result.get('url', 'N/A')}")
                print(f"📎 Status: {result.get('business_status', 'N/A')}")
                
                if all_reviews:
                    print(f"\n📝 Processing {len(all_reviews)} reviews:")
                    
                    # Sort reviews by employment relevance score
                    scored_reviews = []
                    for review in all_reviews:
                        highlighted_text, score, terms = highlight_employment_terms(review.get('text', ''))
                        scored_reviews.append((review, highlighted_text, score, terms))
                    
                    # Sort by score (highest first)
                    scored_reviews.sort(key=lambda x: x[2], reverse=True)
                    
                    # Display reviews
                    for i, (review, highlighted_text, score, terms) in enumerate(scored_reviews, 1):
                        print(f"\n=== Review {i} ===")
                        print(f"👤 Author: {review.get('author_name', 'Anonymous')}")
                        print(f"⭐ Rating: {review.get('rating', 'N/A')} stars")
                        print(f"🕒 Time: {review.get('relative_time_description', 'N/A')}")
                        print(f"📊 Employment Relevance Score: {score}")
                        if terms:
                            print(f"🔍 Employment Terms Found: {', '.join(terms)}")
                        print(f"💬 Review text:")
                        print(highlighted_text)
                        print("=" * 80)
                    
                    # Save reviews to CSV
                    print("\n💾 Saving reviews to CSV...")
                    save_to_csv(result.get('name', 'Pure Sunfarms'), all_reviews)
                    print("✅ Reviews saved successfully!")
                    
                else:
                    print("\n❌ No reviews available in the API")
                    
            except Exception as e:
                print(f"❌ Error getting place details: {str(e)}")
                print("\n🔧 Error Details:")
                print(f"Place ID being used: {place['place_id']}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                print(f"Stack trace:\n{traceback.format_exc()}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Run the scraper
    asyncio.run(run_scraper())

if __name__ == "__main__":
    main() 