"""
Notification system implementation
"""
from telegram import Bot
from telegram.error import TelegramError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import BookingModel, BookingStatusEnum, TenantModel
from utils.logger import get_logger
from apscheduler.schedulers.background import BackgroundScheduler
from config import config
import pytz

logger = get_logger("notification_system")


class NotificationScheduler:
    """Schedule and send notifications"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = BackgroundScheduler(timezone=pytz.UTC)
    
    def start(self):
        """Start scheduler"""
        # Schedule booking reminders - every 30 minutes
        self.scheduler.add_job(
            self.send_reminders,
            'interval',
            minutes=30,
            id='booking_reminders'
        )
        
        # Schedule trial expiry notifications - daily at 10 AM
        self.scheduler.add_job(
            self.notify_trial_expiry,
            'cron',
            hour=10,
            minute=0,
            id='trial_expiry'
        )
        
        # Schedule subscription expiry notifications - daily
        self.scheduler.add_job(
            self.notify_subscription_expiry,
            'cron',
            hour=9,
            minute=0,
            id='subscription_expiry'
        )
        
        self.scheduler.start()
        logger.info("Notification scheduler started")
    
    def stop(self):
        """Stop scheduler"""
        self.scheduler.shutdown()
        logger.info("Notification scheduler stopped")
    
    async def send_reminders(self):
        """Send booking reminders for tomorrow"""
        db = SessionLocal()
        try:
            tomorrow = datetime.now().date() + timedelta(days=1)
            
            # Get bookings for tomorrow that haven't been reminded
            bookings = db.query(BookingModel).filter(
                BookingModel.booking_date == tomorrow,
                BookingModel.status == BookingStatusEnum.CONFIRMED,
                BookingModel.reminder_sent == False
            ).all()
            
            for booking in bookings:
                try:
                    message = f"""
⏰ تذكير بالموعد

📅 موعدك غداً:
🏪 الصالون: {booking.tenant.salon_name}
💇 الخدمة: {booking.service.name if booking.service else 'خدمة'}
⏰ الوقت: {booking.booking_time}
📍 العنوان: {booking.tenant.address}

📱 تأكد من حضورك!
"""
                    
                    await self.bot.send_message(
                        chat_id=booking.customer.telegram_id,
                        text=message
                    )
                    
                    booking.reminder_sent = True
                    booking.reminder_sent_at = datetime.utcnow()
                    db.commit()
                    
                    logger.info(f"Reminder sent for booking {booking.id}")
                    
                except TelegramError as e:
                    logger.error(f"Failed to send reminder: {e}")
        
        except Exception as e:
            logger.error(f"Error sending reminders: {e}")
        finally:
            db.close()
    
    async def notify_trial_expiry(self):
        """Notify tenants with expiring trial"""
        db = SessionLocal()
        try:
            # Get tenants with trial expiring in 2 days
            cutoff = datetime.utcnow() + timedelta(days=2)
            
            expiring_trials = db.query(TenantModel).filter(
                TenantModel.is_trial == True,
                TenantModel.subscription_end <= cutoff,
                TenantModel.subscription_end > datetime.utcnow()
            ).all()
            
            for tenant in expiring_trials:
                try:
                    days_left = (tenant.subscription_end - datetime.utcnow()).days
                    
                    message = f"""
🆓 انتبه: الفترة التجريبية تنتهي قريباً!

📊 الخطة: تجريبية
⏰ تنتهي في: {days_left} أيام

قم بترقية خطتك الآن:
/pay

📞 للمساعدة: تواصل معنا
"""
                    
                    await self.bot.send_message(
                        chat_id=tenant.owner_telegram_id,
                        text=message
                    )
                    
                    logger.info(f"Trial expiry notification sent to {tenant.tenant_id}")
                    
                except TelegramError as e:
                    logger.error(f"Failed to send trial notification: {e}")
        
        except Exception as e:
            logger.error(f"Error notifying trial expiry: {e}")
        finally:
            db.close()
    
    async def notify_subscription_expiry(self):
        """Notify tenants with expiring subscriptions"""
        db = SessionLocal()
        try:
            # Get tenants with subscription expiring in 7 days
            cutoff = datetime.utcnow() + timedelta(days=7)
            
            expiring_subs = db.query(TenantModel).filter(
                TenantModel.subscription_plan != "lifetime",
                TenantModel.subscription_end <= cutoff,
                TenantModel.subscription_end > datetime.utcnow()
            ).all()
            
            for tenant in expiring_subs:
                try:
                    days_left = (tenant.subscription_end - datetime.utcnow()).days
                    
                    message = f"""
⚠️ اشتراكك ينتهي قريباً!

📊 الخطة: {tenant.subscription_plan.upper()}
⏰ ينتهي في: {days_left} أيام

قم بتجديد الاشتراك الآن:
/pay

🔔 لن تفقد أي خدمات إذا جددت في الوقت المناسب
"""
                    
                    await self.bot.send_message(
                        chat_id=tenant.owner_telegram_id,
                        text=message
                    )
                    
                    logger.info(f"Subscription expiry notification sent to {tenant.tenant_id}")
                    
                except TelegramError as e:
                    logger.error(f"Failed to send subscription notification: {e}")
        
        except Exception as e:
            logger.error(f"Error notifying subscription expiry: {e}")
        finally:
            db.close()
