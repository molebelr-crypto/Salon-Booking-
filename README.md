# Salon Booking System - Telegram Bot

Production-ready Telegram-based SaaS Salon Booking System with multi-tenant architecture.

## Features

- **Customer Flow**: Book appointments, view services, contact salon
- **Owner Panel**: Manage bookings, staff, services, working hours, subscriptions
- **Admin Panel**: Manage salons, payments, subscriptions, broadcasting
- **Multi-tenant Architecture**: Complete data isolation per salon
- **Subscription Plans**: Trial (14 days free), Basic, Standard, Premium, Lifetime
- **Payment System**: Manual approval via Zain Cash and Bank Transfer
- **Booking Management**: Status tracking, reminders, waiting list
- **CRM**: Customer data, visit tracking, loyalty system
- **Referral System**: 1 free month per referral
- **Promo Codes**: Percentage and fixed discounts
- **Loyalty Rewards**: Discounts based on tenure
- **Notifications**: Booking confirmations, reminders, alerts
- **Vacation Mode**: Block dates and temporary closure
- **Branches Support** (Premium): Multiple salon locations
- **Feature Flags**: Enable/disable features per salon
- **Comprehensive Logging**: All activities tracked
- **Backup & Restore**: Automatic backups

## Technology Stack

- **Python 3.9+**
- **Telegram Bot API** (python-telegram-bot 21.0.1)
- **SQLAlchemy** (Database ORM)
- **PostgreSQL/SQLite** (Database)
- **Redis** (Caching & Sessions)
- **JWT** (Authentication)

## Project Structure

```
├── main.py                      # Main application entry point
├── config.py                    # Configuration management
├── database.py                  # Database connection & session
├── models.py                    # SQLAlchemy models
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── handlers/
│   ├── __init__.py
│   ├── customer_handlers.py    # Customer flow handlers
│   ├── owner_handlers.py       # Owner panel handlers
│   └── admin_handlers.py       # Admin panel handlers
└── utils/
    ├── __init__.py
    ├── logger.py               # Logging configuration
    ├── tenant_context.py       # Multi-tenant context management
    └── permissions.py          # Permission and access control
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/molebelr-crypto/Salon-Booking-.git
cd Salon-Booking-
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the bot:
```bash
python main.py
```

## Configuration

Edit `.env` file with your settings:

```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_admin_id
DATABASE_URL=postgresql://user:password@localhost:5432/salon_booking
ENVIRONMENT=development
```

## API Configuration

Telegram Bot Token: `8571254471:AAGRrXnN5HyNAaj9qfuYeN7KnABAbtbHY_A`

⚠️ **IMPORTANT**: This token is now public. Please regenerate it in BotFather to keep your bot secure:
1. Message @BotFather on Telegram
2. Select your bot
3. Choose "Regenerate Token"

## Database Models

- **TenantModel**: Salon organizations with multi-tenant isolation
- **ServiceModel**: Services offered by salon
- **StaffModel**: Barbers/staff members
- **BookingModel**: Customer appointments
- **CustomerModel**: Customer CRM data
- **SubscriptionHistoryModel**: Subscription tracking
- **PaymentModel**: Payment records
- **PromoCodeModel**: Discount codes
- **WaitingListModel**: Waiting list management
- **BranchModel**: Salon branches (Premium feature)
- **LogModel**: Activity logs
- **SettingsModel**: Tenant settings

## Subscription Plans

| Plan | Price | Features |
|------|-------|----------|
| Trial | Free | 14 days, 1 barber, 100 bookings |
| Basic | $9.99/mo | 1 barber, basic features |
| Standard | $19.99/mo | 5 barbers, reminders, analytics |
| Premium | $49.99/mo | Unlimited barbers, branches, reports |
| Lifetime | $999 | One-time, unlimited everything |

## Usage

### For Customers
- `/start` - Show main menu
- Book appointments
- View services
- Contact salon
- View your bookings

### For Salon Owners
- `/owner` - Access owner panel
- Manage bookings
- Manage services and staff
- Set working hours
- Check subscription status
- View statistics

### For Admins
- `/admin` - Access admin panel (ADMIN_ID only)
- Manage all salons
- Process payments
- Monitor subscriptions
- Send broadcasts

## Development Notes

### Adding Features

1. Add database models in `models.py`
2. Create handlers in `handlers/` directory
3. Add routes in main bot file
4. Update permissions if needed in `utils/permissions.py`

### Extending Multi-Tenant

The system uses SQLAlchemy relationships and context variables for multi-tenant isolation. Always filter queries by `tenant_id` to ensure data isolation.

## Security Considerations

- ✅ Multi-tenant data isolation
- ✅ Permission-based access control
- ✅ Admin authorization checks
- ✅ Activity logging
- ✅ Subscription validation
- ⚠️ Regenerate bot token (current one is exposed)
- ⚠️ Use strong JWT secrets in production
- ⚠️ Enable HTTPS for webhooks in production

## Monitoring & Logs

Logs are stored in `logs/app.log` with rotation every 10MB. Check logs for:
- User activities
- Booking operations
- Payment processing
- Admin actions
- Errors and exceptions

## API Integration

The system is designed to support:
- Mobile app APIs
- Web dashboard
- WhatsApp integration
- Third-party booking systems

## Support & Contributing

For issues, feature requests, or contributions, please open an issue on GitHub.

## License

MIT License - See LICENSE file for details

---

**Next Steps:**
1. Regenerate the bot token in BotFather
2. Complete handler implementations
3. Add onboarding wizard flow
4. Implement payment processing
5. Add SMS/Email notifications
6. Create admin approval workflows
