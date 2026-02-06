# WIMA Serenity Gardens - Backend API

Backend API for WIMA Serenity Gardens guest house website built with Flask, PostgreSQL, and Flask-Mail.

## 🏗️ Tech Stack

- **Framework:** Flask 2.3
- **Database:** PostgreSQL 14+
- **ORM:** SQLAlchemy
- **Migrations:** Flask-Migrate
- **Email:** Flask-Mail
- **CORS:** Flask-CORS
- **Server:** Gunicorn (production)

## 📁 Project Structure

```
wima-backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration classes
│   ├── models/              # Database models
│   │   ├── room.py
│   │   ├── inquiry.py
│   │   └── event_inquiry.py
│   ├── routes/              # API endpoints
│   │   ├── rooms.py
│   │   ├── inquiries.py
│   │   └── contact.py
│   └── services/
│       └── email.py         # Email notifications
├── migrations/              # Database migrations
├── seed_data.py            # Database seeding script
├── run.py                  # Application entry point
├── Pipfile                 # Dependencies
├── .env.example            # Environment variables template
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL 14+
- pipenv (install with `pip install pipenv`)

### 1. Clone and Navigate

```bash
cd wima-backend
```

### 2. Install Dependencies

```bash
pipenv install
```

### 3. Activate Virtual Environment

```bash
pipenv shell
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update these variables:

```env
# Database (update if needed)
DATABASE_URL=postgresql://localhost/wima_serenity_dev

# Email (use your actual email credentials)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password

# Business contacts
BUSINESS_EMAIL=info@wimaserenitygardens.com
BUSINESS_PHONE=+254700000000
BUSINESS_WHATSAPP=+254700000000
```

**Note for Gmail users:** Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

### 5. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE wima_serenity_dev;

# Exit psql
\q
```

### 6. Run Database Migrations

```bash
# Initialize migrations (only needed once)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 7. Seed the Database

```bash
python seed_data.py
```

This will add all 7 rooms to the database.

### 8. Run the Application

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## 🧪 Testing the API

### Health Check

```bash
curl http://localhost:5000/api/health
```

### Get All Rooms

```bash
curl http://localhost:5000/api/rooms
```

### Get Featured Rooms

```bash
curl http://localhost:5000/api/rooms/featured
```

### Get Single Room

```bash
curl http://localhost:5000/api/rooms/premier-room-1
```

### Submit Booking Inquiry

```bash
curl -X POST http://localhost:5000/api/inquiries \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+254700000000",
    "inquiry_type": "booking",
    "room_id": 1,
    "check_in": "2026-03-15",
    "check_out": "2026-03-17",
    "guests": 2,
    "message": "I would like to book this room for a weekend getaway."
  }'
```

### Submit Event Inquiry

```bash
curl -X POST http://localhost:5000/api/inquiries/event \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+254700000000",
    "event_type": "wedding",
    "event_date": "2026-06-20",
    "guest_count": 150,
    "venue_preference": "field_1",
    "message": "Looking to book the venue for our wedding reception."
  }'
```

### Submit Contact Form

```bash
curl -X POST http://localhost:5000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Brown",
    "email": "alice@example.com",
    "phone": "+254700000000",
    "subject": "General Inquiry",
    "message": "What are your check-in and check-out times?"
  }'
```

## 📡 API Endpoints

### Rooms

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rooms` | Get all active rooms |
| GET | `/api/rooms/featured` | Get featured rooms (homepage) |
| GET | `/api/rooms/<slug>` | Get single room by slug |
| GET | `/api/rooms/type/<type>` | Get rooms by type |

### Inquiries

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/inquiries` | Submit booking inquiry |
| POST | `/api/inquiries/event` | Submit event inquiry |

### Contact

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/contact` | Submit contact form |

## 🗄️ Database Schema

### Rooms

- id (Primary Key)
- name, slug, type
- description, capacity
- price_per_night, breakfast_included
- amenities (JSON), images (JSON)
- is_featured, is_active
- created_at, updated_at

### Inquiries

- id (Primary Key)
- name, email, phone
- inquiry_type, room_id (Foreign Key)
- check_in, check_out, guests
- message, status
- created_at

### Event Inquiries

- id (Primary Key)
- name, email, phone
- event_type, event_date
- guest_count, venue_preference
- message, status
- created_at

## 📧 Email Notifications

The system automatically sends emails for:

1. **Booking Inquiries**
   - Owner receives inquiry details
   - Guest receives confirmation

2. **Event Inquiries**
   - Owner receives event request
   - Client receives confirmation

3. **Contact Form**
   - Owner receives message
   - Sender receives confirmation

## 🔧 Common Commands

```bash
# Activate virtual environment
pipenv shell

# Install new package
pipenv install package-name

# Run development server
python run.py

# Create new migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# Seed database
python seed_data.py

# Run tests (Phase 2)
pytest
```

## 🌍 Deployment (Render)

### 1. Create `render.yaml`

```yaml
services:
  - type: web
    name: wima-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn run:app"
    envVars:
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: wima-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: MAIL_USERNAME
        sync: false
      - key: MAIL_PASSWORD
        sync: false

databases:
  - name: wima-db
    databaseName: wima_serenity_prod
    user: wima_user
```

### 2. Generate `requirements.txt`

```bash
pipenv requirements > requirements.txt
```

### 3. Push to GitHub and Connect to Render

Render will automatically deploy when you push to your main branch.

## 🛡️ Security Checklist

- [x] Environment variables for secrets
- [x] Input validation on all forms
- [x] Parameterized SQL queries (SQLAlchemy ORM)
- [x] CORS configuration
- [ ] Rate limiting (Phase 2)
- [ ] HTTPS enforcement (production)

## 📝 Notes

- Default admin features disabled for MVP
- M-Pesa integration planned for Phase 2
- All dates use ISO format (YYYY-MM-DD)
- Prices in Kenyan Shillings (KSh)
- Breakfast included in all room prices

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check if PostgreSQL is running
brew services list

# Start PostgreSQL
brew services start postgresql@14
```

### Migration Errors

```bash
# Delete migrations folder and start fresh
rm -rf migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Email Not Sending

- Verify Gmail App Password is correct
- Check that "Less secure app access" is enabled (or use App Password)
- Ensure firewall isn't blocking port 587

## 📞 Support

For issues or questions, contact the development team.

---

**WIMA Serenity Gardens** - Guest House | Leisure Gardens | Event Venue