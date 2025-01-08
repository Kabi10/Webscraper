import os
from dotenv import load_dotenv
import googlemaps
from datetime import datetime

def main():
    # Load environment variables
    load_dotenv('.env.local')
    
    # Get API key
    api_key = os.getenv('NEXT_PUBLIC_GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("Google Maps API key not found in .env.local")
    
    # Initialize client
    gmaps = googlemaps.Client(key=api_key)
    
    print(f"🔑 Using API key: {api_key[:4]}...{api_key[-4:]}")
    print("\n🔍 Testing API with a simple request...")
    
    try:
        # Make a simple request that costs minimal quota
        result = gmaps.find_place(
            input="BZAM Management Inc.",
            input_type="textquery",
            fields=["place_id"]
        )
        
        print("\n✅ API is responding!")
        print(f"Response status: {result.get('status')}")
        
        # Note: For actual quota information, you need to:
        print("\n📊 To check detailed quota usage:")
        print("1. Go to: https://console.cloud.google.com/apis/dashboard")
        print("2. Select your project")
        print("3. Click on 'Places API' under 'APIs and Services'")
        print("4. View the Quotas tab")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 