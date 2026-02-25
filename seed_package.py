"""
Seed script for the Home Away From Home package.
Run: python seed_package.py
"""
from app import create_app, db
from app.models.package import Package


def seed_home_away_package():
    app = create_app('development')

    with app.app_context():
        existing = Package.query.filter_by(slug='home-away-from-home').first()
        if existing:
            print('Package already exists — skipping.')
            return

        package = Package(
            name='Home Away From Home Package',
            slug='home-away-from-home',
            tagline='One estate. All yours.',
            short_description=(
                'Reserve all seven rooms at WIMA Serenity Gardens for the exclusive use of your group. '
                'Complete privacy, lush gardens, and breakfast for everyone included — the whole estate, just for you. '
                'Perfect for families, reunions, corporate retreats, and wedding parties.'
            ),
            long_description=(
                'Imagine waking up to birdsong with no other guests in sight — just your people, your pace, '
                'and the whole estate to yourselves. The Home Away From Home Package gives your group exclusive '
                'use of all seven of our rooms: three Standard Doubles, two Premier Rooms, our secluded Garden '
                'Cottage, and the Family Room. Breakfast is served for everyone each morning, the tropical gardens '
                'are yours to roam freely, and parking is included. Whether you\'re gathering the family for a '
                'reunion, celebrating a milestone, hosting a small corporate retreat, or settling in a wedding '
                'party the night before the big day, this is more than a booking — it\'s your own private retreat '
                'in Kenya\'s beautiful tea country, with all the warmth and hospitality WIMA is known for.'
            ),
            price_per_night=40000,
            original_price=42500,
            rooms_included=[
                '3x Standard Double Rooms',
                '2x Premier Rooms',
                '1x Garden Cottage',
                '1x Family Room',
            ],
            capacity=20,
            breakfast_included=True,
            amenities=[
                'All 7 Rooms',
                'Exclusive Property Access',
                'Tropical Gardens',
                'Free Parking',
                'Breakfast for All Guests',
            ],
            benefits=[
                'Save KSh 2,500 vs. booking all rooms separately',
                'Complete privacy — no other guests, the whole property is yours',
                'Breakfast included for every guest, every morning',
                'Ideal for families, reunion groups, and wedding parties',
                'Accommodates up to 20 guests across 7 rooms',
            ],
            images=[
                '/images/large_aerial_view.PNG',
                '/images/house_picture_from_garden.png',
                '/images/house_pic_from_out_with_table.jpeg',
            ],
            is_featured=True,
            is_active=True,
        )

        db.session.add(package)
        db.session.commit()

        print('Home Away From Home package created successfully.')
        print(f'  Price:    KSh {package.price_per_night:,}/night')
        print(f'  Savings:  KSh {package.get_savings():,} ({package.get_discount_percentage()}% off)')
        print(f'  Capacity: {package.capacity} guests')


if __name__ == '__main__':
    seed_home_away_package()
