#!/usr/bin/env python3
"""
Specialized test script for image retrieval functionality.
Tests both the backend image endpoint and S3 credentials.
"""
import requests
import json

def test_backend_api():
    """Test that backend returns graphics cards with image URLs"""
    print("=== Testing Backend API ===")
    try:
        resp = requests.get("http://localhost:8000/graphic-cards", timeout=5)
        if resp.status_code != 200:
            print(f"❌ Backend API error: {resp.status_code}")
            return []
        
        cards = resp.json()
        print(f"✅ Backend returned {len(cards)} graphics cards")
        
        # Show sample data
        if cards:
            sample = cards[0]
            print(f"📋 Sample card: {sample['name']}")
            print(f"💰 Price: €{sample['price']}")
            print(f"🖼️  Image URL: {sample['imageUrl']}")
        
        return cards
    except Exception as e:
        print(f"❌ Backend API failed: {e}")
        return []

def test_image_endpoints(cards):
    """Test image retrieval for sample cards"""
    print("\n=== Testing Image Endpoints ===")
    
    if not cards:
        print("❌ No cards to test images for")
        return
    
    working_count = 0
    total_count = 0
    
    # Test first 5 cards
    for i, card in enumerate(cards[:5]):
        image_url = card.get('imageUrl', '')
        if not image_url:
            continue
            
        # Extract filename from path
        if 'cdn-images/' in image_url:
            filename = image_url.split('cdn-images/')[-1]
            test_url = f"http://localhost:8000/images/{filename}"
            
            try:
                resp = requests.get(test_url, timeout=5, allow_redirects=False)
                total_count += 1
                
                if resp.status_code == 307:  # Temporary Redirect to S3
                    print(f"🔄 {filename}: Redirecting to S3 (status: {resp.status_code})")
                    # Follow the redirect to test actual image access
                    if 'location' in resp.headers:
                        s3_url = resp.headers['location']
                        s3_resp = requests.get(s3_url, timeout=5)
                        if s3_resp.status_code == 200:
                            print(f"✅ {filename}: S3 image accessible")
                            working_count += 1
                        else:
                            print(f"❌ {filename}: S3 access failed ({s3_resp.status_code})")
                elif resp.status_code == 200:
                    print(f"✅ {filename}: Direct access working")
                    working_count += 1
                else:
                    print(f"❌ {filename}: Failed ({resp.status_code})")
                    
            except Exception as e:
                total_count += 1
                print(f"❌ {filename}: Error - {e}")
    
    if total_count > 0:
        success_rate = working_count / total_count
        print(f"\n📊 Image Test Results: {working_count}/{total_count} working ({success_rate:.1%})")
        return success_rate > 0.5
    else:
        print("\n❌ No images found to test")
        return False

def test_local_images():
    """Check if local images exist as fallback"""
    print("\n=== Testing Local Image Fallback ===")
    import os
    
    local_images_path = "cdn-images"
    if os.path.exists(local_images_path):
        image_files = [f for f in os.listdir(local_images_path) if f.endswith(('.jpg', '.png'))]
        print(f"📁 Found {len(image_files)} local images in {local_images_path}/")
        
        if image_files:
            print("🖼️  Sample images:")
            for img in image_files[:3]:
                print(f"   - {img}")
        return len(image_files) > 0
    else:
        print(f"❌ Local images directory not found: {local_images_path}")
        return False

def main():
    print("🔍 PC Builder Image Retrieval Test")
    print("=" * 50)
    
    # Test backend API
    cards = test_backend_api()
    
    # Test image endpoints
    images_working = test_image_endpoints(cards)
    
    # Test local images
    local_images_exist = test_local_images()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if cards:
        print("✅ Backend API: Working")
        print(f"   {len(cards)} graphics cards loaded from local CSV")
    else:
        print("❌ Backend API: Failed")
    
    if images_working:
        print("✅ Image Retrieval: Working")
    else:
        print("❌ Image Retrieval: Failed (likely S3 credential issue)")
        print("   Fix: Update AWS_SECRET_ACCESS_KEY in .env file")
    
    if local_images_exist:
        print("✅ Local Images: Available as fallback")
    else:
        print("❌ Local Images: Not found")
    
    print("\n🔧 Next Steps:")
    if not images_working:
        print("1. Update AWS credentials in .env file")
        print("2. Restart backend to pick up new credentials")
        print("3. Test image retrieval again")
    else:
        print("1. All image functionality is working!")

if __name__ == "__main__":
    main()
