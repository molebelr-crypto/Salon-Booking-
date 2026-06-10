"""
Updated main.py with all handlers integrated
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from config import config
from database import init_db
from utils.logger import get_logger

from handlers import (
    customer_handlers,
    owner_handlers,
    admin_handlers,
    onboarding,
    booking_flow,
    payments,
    admin_payments
)
from services.notification_scheduler import NotificationScheduler

logger = get_logger("main")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    user = update.effective_user
    logger.info(f"User started bot: {user.id}")
    
    await customer_handlers.start(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    help_text = """
🏪 نظام حجز المواعيد - مرحباً بك!

📱 **الأوامر الرئيسية:**

👤 **للعملاء:**
/start - القائمة الرئيسية
/book - حجز موعد جديد
/myBookings - عرض حجوزاتي
/help - المساعدة

💼 **لأصحاب الصالونات:**
/newowner - تسجيل صالون جديد
/owner - لوحة التحكم
/pay - الدفع والاشتراكات

👑 **للمسؤولين:**
/admin - لوحة الإدارة (مسؤول فقط)

❓ **أخرى:**
/contact - التواصل معنا
/about - عن التطبيق

🎯 **ابدأ الآن:**
- إذا كنت عميل: اضغط /book
- إذا كنت صاحب صالون: اضغط /newowner
"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """About command"""
    about_text = """
📋 عن التطبيق

**نظام حجز المواعيد - Salon Booking SaaS**

🎯 التطبيق الأول والأفضل لإدارة حجوزات الصالونات بسهولة

✨ **الميزات:**
✅ حجز مواعيد سهل وسريع
✅ إدارة الموظفين والخدمات
✅ تقارير وإحصائيات مفصلة
✅ نظام دفع آمن
✅ إشعارات تلقائية
✅ إدارة العملاء

💰 **خطط الاشتراك:**
🆓 تجريبية - 14 يوم مجاني
📚 أساسية - $9.99/شهر
⭐ معيارية - $19.99/شهر
🚀 احترافية - $49.99/شهر
👑 مدى الحياة - $999 مرة واحدة

📞 **التواصل:**
Email: support@salonbooking.com
Telegram: @SalonBookingSupport

🌐 **الموقع:**
www.salonbooking.com

© 2026 Salon Booking - جميع الحقوق محفوظة
"""
    
    await update.message.reply_text(about_text, parse_mode="Markdown")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log and handle errors"""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    # Send error message to admin
    if config.ADMIN_ID:
        try:
            error_msg = str(context.error)[:200]
            await context.bot.send_message(
                chat_id=config.ADMIN_ID,
                text=f"⚠️ خطأ في البوت:\n{error_msg}"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin of error: {e}")


async def post_init(app: Application):
    """Run after bot is initialized"""
    logger.info("✅ Bot initialized successfully")
    logger.info("🔔 Starting notification scheduler...")
    
    try:
        # Initialize notification scheduler
        notification_scheduler = NotificationScheduler(app.bot)
        notification_scheduler.start()
        
        # Store in app context for later access
        app.bot_data['notification_scheduler'] = notification_scheduler
        
        logger.info("✅ Notification scheduler started")
    except Exception as e:
        logger.error(f"Failed to start notification scheduler: {e}")


def create_app() -> Application:
    """Create and configure the Telegram bot application"""
    
    logger.info(f"🚀 Creating bot application in {config.ENVIRONMENT} mode...")
    
    # Create application
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # Set post_init callback
    app.post_init = post_init
    
    # ==================== COMMANDS ====================
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    
    # ==================== ONBOARDING ====================
    app.add_handler(onboarding.get_onboarding_handler())
    
    # ==================== BOOKING FLOW ====================
    app.add_handler(booking_flow.get_booking_handler())
    
    # ==================== PAYMENTS ====================
    app.add_handler(payments.get_payment_handler())
    
    # ==================== OWNER PANEL ====================
    app.add_handler(CommandHandler("owner", owner_handlers.owner_panel))
    app.add_handler(CallbackQueryHandler(
        owner_handlers.button_handler,
        pattern="^owner_"
    ))
    
    # ==================== ADMIN PANEL ====================
    app.add_handler(CommandHandler("admin", admin_handlers.admin_panel))
    app.add_handler(CallbackQueryHandler(
        admin_handlers.button_handler,
        pattern="^admin_"
    ))
    
    # ==================== ADMIN PAYMENTS ====================
    app.add_handler(CallbackQueryHandler(
        admin_payments.approve_payment,
        pattern="^approve_payment_"
    ))
    app.add_handler(CallbackQueryHandler(
        admin_payments.reject_payment,
        pattern="^reject_payment_"
    ))
    
    # ==================== CUSTOMER HANDLERS ====================
    app.add_handler(CallbackQueryHandler(
        customer_handlers.button_handler,
        pattern="^customer_"
    ))
    
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        customer_handlers.message_handler
    ))
    
    # ==================== ERROR HANDLER ====================
    app.add_error_handler(error_handler)
    
    return app


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("🏪 نظام حجز المواعيد - Salon Booking System")
    logger.info("=" * 60)
    logger.info(f"🌍 البيئة: {config.ENVIRONMENT}")
    logger.info(f"🔧 وضع التطوير: {config.DEBUG}")
    logger.info(f"📊 مستوى التسجيل: {config.LOG_LEVEL}")
    logger.info("=" * 60)
    
    try:
        # Initialize database
        logger.info("💾 Initializing database...")
        init_db()
        logger.info("✅ Database initialized successfully")
        
        # Create application
        logger.info("🤖 Creating bot application...")
        app = create_app()
        logger.info("✅ Bot application created successfully")
        
        # Start the bot
        if config.WEBHOOK_URL:
            logger.info(f"🌐 Starting with webhooks")
            logger.info(f"📍 URL: {config.WEBHOOK_URL}{config.WEBHOOK_PATH}")
            logger.info(f"🔒 Using HTTPS webhook")
            
            app.run_webhook(
                listen=config.SERVER_HOST,
                port=config.SERVER_PORT,
                url_path=config.WEBHOOK_PATH,
                webhook_url=f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}"
            )
        else:
            logger.info("📱 Starting with polling mode")
            logger.info(f"🔌 Server: {config.SERVER_HOST}:{config.SERVER_PORT}")
            logger.info("👂 Listening for updates...")
            
            app.run_polling(allowed_updates=Update.ALL_TYPES)
            
    except Exception as e:
        logger.critical(f"❌ Failed to start bot: {e}")
        raise
    finally:
        logger.info("🛑 Bot stopped")


if __name__ == "__main__":
    main()
