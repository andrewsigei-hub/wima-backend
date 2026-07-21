"""
Seed database with initial room data for WIMA Serenity Gardens.
"""

# This one is still a WIP - Room details are a little thin
import os
import sys
from app import create_app, db
from app.models.room import Room

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def seed_rooms():
    """Seed the database with actual room data."""
    
    # Breakfast menu (KSh 500)
    breakfast_menu = [
        "Tea/Coffee/Milk",
        "Mandazi/Cereals/Bread",
        "Fried egg/Boiled egg",
        "Sausage",
        "Mixed vegetables"
    ]
    
    rooms_data = [
        # 3 Deluxe Rooms - KSh 5,000/night
        {
            "name": "Deluxe Room 1",
            "slug": "deluxe-room-1",
            "type": "deluxe",
            "description": "Comfortable deluxe room perfect for couples seeking a cozy retreat in Kericho. Features modern amenities, a double bed, and an en-suite bathroom with hot shower. Enjoy beautiful garden views and peaceful surroundings. Breakfast for 2 guests included in the rate (KSh 500 per person).",
            "capacity": 2,
            "price_per_night": 5000,
            "breakfast_included": True,
            "amenities": [
                "Double bed",
                "En-suite bathroom",
                "Hot shower",
                "WiFi",
                "Garden view",
                "Work desk",
                "Wardrobe",
                "Complimentary toiletries",
            ],
            "images": [
                "/images/michelle-room/IMG_4973.JPG",
                "/images/michelle-room/IMG_4974.JPG",
                "/images/michelle-room/IMG_4975.JPG"
            ],
            "is_featured": True,
            "is_active": True
        },
        {
            "name": "Deluxe Room 2",
            "slug": "deluxe-room-2",
            "type": "deluxe",
            "description": "Well-appointed deluxe room offering excellent value and comfort for your Kericho stay. Tastefully furnished with attention to detail, featuring a comfortable double bed and all essential amenities. Perfect for business travelers or couples exploring the tea country. Breakfast for 2 guests included.",
            "capacity": 2,
            "price_per_night": 5000,
            "breakfast_included": True,
            "amenities": [
                "Double bed",
                "En-suite bathroom",
                "Hot shower",
                "WiFi",
                "Work desk",
                "Wardrobe",
                "Complimentary toiletries",
            ],
            "images": [
                "/images/single-room/IMG_4976.JPG",
                "/images/single-room/IMG_4977.JPG",
                "/images/single-room/IMG_4978.JPG"
            ],
            "is_featured": True,
            "is_active": True
        },
        {
            "name": "Deluxe Room 3",
            "slug": "deluxe-room-3",
            "type": "deluxe",
            "description": "Inviting deluxe room designed for maximum comfort and relaxation. Clean, cozy, and equipped with everything you need for a pleasant stay. Enjoy modern conveniences including WiFi and DSTV, plus stunning views of our serene gardens. Breakfast for 2 guests included in the room rate.",
            "capacity": 2,
            "price_per_night": 5000,
            "breakfast_included": True,
            "amenities": [
                "Double bed",
                "En-suite bathroom",
                "Hot shower",
                "WiFi",
                "Work desk",
                "Wardrobe",
                "Complimentary toiletries",
            ],
            "images": [],
            "is_featured": False,
            "is_active": True
        },
        # 1 Double Room - KSh 6,000/night
        {
            "name": "Double Room",
            "slug": "double-room",
            "type": "double",
            "description": "Spacious double room ideal for couples or small families seeking extra comfort. Features a large double bed, ample storage space, and a modern en-suite bathroom. Perfect for extended stays in Kericho's beautiful tea country. Room includes breakfast for 2 guests (valued at KSh 1,000).",
            "capacity": 2,
            "price_per_night": 6000,
            "breakfast_included": True,
            "amenities": [
                "Large double bed",
                "En-suite bathroom",
                "Hot shower",
                "WiFi",
                "Large wardrobe",
                "Work desk",
                "Complimentary toiletries"
            ],
            "images": [
                "/images/double-room/IMG_4935.JPG",
                "/images/double-room/IMG_4936.JPG",
                "/images/double-room/IMG_4937.JPG",
                "/images/double-room/IMG_4938.JPG"
            ],
            "is_featured": True,
            "is_active": True
        },
        # 2 Executive Rooms - KSh 6,000/night
        {
            "name": "Executive Room 1",
            "slug": "executive-room-1",
            "type": "executive",
            "description": "Premium executive room offering superior comfort and style for discerning guests. Elegantly furnished with high-quality bedding, modern amenities, and a spacious en-suite bathroom. Ideal for business travelers or those seeking an elevated experience. Includes breakfast for 2 guests.",
            "capacity": 2,
            "price_per_night": 6000,
            "breakfast_included": True,
            "amenities": [
                "King-size bed",
                "Premium bedding",
                "En-suite bathroom",
                "Hot shower",
                "WiFi",
                "TV with DSTV",
                "Private balcony",
                "Garden view",
                "Executive work desk",
                "Large wardrobe",
                "Complimentary toiletries",
                "Breakfast for 2 included"
            ],
            "images": [
                "/images/Master bedroom/IMG_4922.JPG",
                "/images/Master bedroom/IMG_4923.JPG",
                "/images/Master bedroom/IMG_4924.JPG",
                "/images/Master bedroom/IMG_4925.JPG"
            ],
            "is_featured": True,
            "is_active": True
        },
        {
            "name": "Executive Room 2",
            "slug": "executive-room-2",
            "type": "executive",
            "description": "Sophisticated executive room designed for maximum comfort and productivity. Features premium furnishings, a king-size bed, and a private balcony overlooking our beautiful gardens. Perfect for business meetings or romantic getaways. Breakfast for 2 guests included in the rate.",
            "capacity": 2,
            "price_per_night": 6000,
            "breakfast_included": True,
            "amenities": [
                "King-size bed",
                "Premium bedding",
                "En-suite bathroom",
                "Hot shower",
                "WiFi",
                "TV with DSTV",
                "Private balcony",
                "Garden view",
                "Executive work desk",
                "Large wardrobe",
                "Complimentary toiletries",
                "Breakfast for 2 included"
            ],
            "images": [
                "/images/andrew-room/IMG_4982.JPG",
                "/images/andrew-room/IMG_4983.JPG",
                "/images/andrew-room/IMG_4984.JPG",
                "/images/andrew-room/IMG_4985.JPG"
            ],
            "is_featured": False,
            "is_active": True
        },
        # 1 Cottage - KSh 7,000/night
        {
            "name": "Garden Cottage",
            "slug": "garden-cottage",
            "type": "cottage",
            "description": "Exclusive standalone cottage offering ultimate privacy and a home-away-from-home experience. Nestled in our lush gardens, this charming cottage features a separate living area, kitchenette, private patio, and premium amenities. Perfect for couples seeking romance or small families wanting space and tranquility. Includes breakfast for 2 guests (KSh 500 per person).",
            "capacity": 3,
            "price_per_night": 7000,
            "breakfast_included": True,
            "amenities": [
                "Queen-size bed",
                "Separate living area",
                "Kitchenette",
                "Mini fridge",
                "En-suite bathroom",
                "Hot shower",
                "WiFi",
                "TV with DSTV",
                "Private patio",
                "Garden view",
                "Outdoor seating",
                "Work desk",
                "Large wardrobe",
                "Complimentary toiletries",
                "Breakfast for 2 included"
            ],
            "images": [
                "/images/cottage/IMG_4948.JPG",
                "/images/cottage/IMG_4949.JPG",
                "/images/cottage/IMG_4950.JPG",
                "/images/cottage/IMG_4951.JPG"
            ],
            "is_featured": True,
            "is_active": True
        }
    ]
    
    print("Starting database seeding...")
    
    # Clear existing rooms (optional - uncomment if you want to start fresh)
    # Room.query.delete()
    # db.session.commit()
    # print("Cleared existing rooms")
    
    # Add rooms
    for room_data in rooms_data:
        # Check if room already exists
        existing_room = Room.query.filter_by(slug=room_data['slug']).first()

        if existing_room:
            existing_room.images = room_data['images']
            print(f"Room '{room_data['name']}' already exists, updated images...")
            continue

        room = Room(**room_data)
        db.session.add(room)
        print(f"Added room: {room_data['name']}")
    
    try:
        db.session.commit()
        print(f"\n✅ Successfully seeded {len(rooms_data)} rooms!")
        
        # Print summary
        total_rooms = Room.query.count()
        featured_rooms = Room.query.filter_by(is_featured=True).count()
        print(f"\nDatabase Summary:")
        print(f"- Total rooms: {total_rooms}")
        print(f"- Featured rooms: {featured_rooms}")
        print(f"- Deluxe rooms: {Room.query.filter_by(type='deluxe').count()} @ KSh 5,000/night")
        print(f"- Double rooms: {Room.query.filter_by(type='double').count()} @ KSh 6,000/night")
        print(f"- Executive rooms: {Room.query.filter_by(type='executive').count()} @ KSh 6,000/night")
        print(f"- Cottage: {Room.query.filter_by(type='cottage').count()} @ KSh 7,000/night")
        print(f"\nBreakfast Info:")
        print(f"- Included for 2 guests with each room")
        print(f"- Value: KSh 500 per person")
        print(f"- Menu: Tea/Coffee/Milk, Mandazi/Cereals/Bread, Fried egg/Boiled egg, Sausage, Mixed Veg")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error seeding database: {str(e)}")
        return False
    
    return True


if __name__ == '__main__':
    # Create app and application context
    app = create_app('development')
    
    with app.app_context():
        seed_rooms()