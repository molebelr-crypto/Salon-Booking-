"""
Payment processing and verification handler
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from database import SessionLocal
from models import TenantModel, PaymentModel, PaymentMethodEnum, PaymentStatusEnum
from services.payments import PaymentManager
from services.subscriptions import SubscriptionManager
from utils.tenant_context import get_tenant_by_owner
from utils.logger import get_logger
from config import config

logger = get_logger("payments")

# Conversation states
PAYMENT_METHOD = 1
PAYMENT_AMOUNT = 2
PAYMENT_PLAN = 3
PAYMENT_DETAILS = 4
PAYMENT_SUBMIT = 5


async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start payment process"""
    user = update.effective_user
    
    db = SessionLocal()
    try:
        tenant = get_tenant_by_owner(user.id)
        
        if not tenant:
            await update.message.reply_text("❌ أنت لست صاحب صالون")
            return ConversationHandler.END
        
        # Show payment methods
        keyboard = [
            [InlineKeyboardButton("💰 Zain Cash", callback_data="method_zain")],
            [InlineKeyboardButton("🏦 تحويل بنكي", callback_data="method_bank")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "💳 طريقة الدفع\n\n"
            "اختر طريقة الدفع:",
            reply_markup=reply_markup
        )
        
        return PAYMENT_METHOD
        
    finally:
        db.close()


async def payment_method_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment method selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "method_zain":
        context.user_data['payment_method'] = PaymentMethodEnum.ZAIN_CASH
        method_name = "Zain Cash"
    else:
        context.user_data['payment_method'] = PaymentMethodEnum.BANK_TRANSFER
        method_name = "تحويل بنكي"
    
    # Show plans
    keyboard = [
        [InlineKeyboardButton("📚 Basic - $9.99/شهر", callback_data="plan_basic")],
        [InlineKeyboardButton("⭐ Standard - $19.99/شهر", callback_data="plan_standard")],
        [InlineKeyboardButton("🚀 Premium - $49.99/شهر", callback_data="plan_premium")],
        [InlineKeyboardButton("👑 Lifetime - $999", callback_data="plan_lifetime")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ طريقة الدفع: {method_name}\n\n"
        f"اختر الخطة:",
        reply_markup=reply_markup
    )
    
    return PAYMENT_PLAN


async def payment_plan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle plan selection"""
    query = update.callback_query
    await query.answer()
    
    plan_map = {
        "plan_basic": ("basic", 9.99),
        "plan_standard": ("standard", 19.99),
        "plan_premium": ("premium", 49.99),
        "plan_lifetime": ("lifetime", 999.00)
    }
    
    plan, amount = plan_map[query.data]
    context.user_data['plan'] = plan
    context.user_data['amount'] = amount
    
    # Show payment details
    if context.user_data['payment_method'] == PaymentMethodEnum.ZAIN_CASH:
        instructions = """
💰 Zain Cash

1️⃣ اتصل بـ: *9625XXXXXXXXXX*
2️⃣ أو استخدم تطبيق Zain Cash
3️⃣ أرسل ${amount} إلى: [MERCHANT_ID]
4️⃣ أرسل رقم المعاملة هنا

⚠️ ملاحظة: قد تستغرق الموافقة 1-2 ساعة
""".format(amount=amount)
    else:
        instructions = f"""
🏦 تحويل بنكي

البيانات البنكية:
اسم الحساب: Salon Booking System
الرقم الحسابي: {config.BANK_TRANSFER_ACCOUNT}

المبلغ: ${amount}

❗ تأكد من الكتابة الصحيحة للبيانات

أرسل رقم المعاملة بعد التحويل
"""
    
    await query.edit_message_text(
        instructions,
        parse_mode="Markdown"
    )
    
    await query.message.reply_text(
        "أرسل رقم المعاملة (Transaction ID):"
    )
    
    return PAYMENT_DETAILS


async def payment_details_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment details submission"""
    transaction_id = update.message.text.strip()
    context.user_data['transaction_id'] = transaction_id
    
    # Show confirmation
    keyboard = [
        [InlineKeyboardButton("✅ تأكيد", callback_data="payment_confirm")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="payment_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    summary = f"""
📋 ملخص الدفع:

طريقة الدفع: {context.user_data['payment_method'].value}
الخطة: {context.user_data['plan'].upper()}
المبلغ: ${context.user_data['amount']}
رقم المعاملة: {transaction_id}

هل البيانات صحيحة؟
"""
    
    await update.message.reply_text(summary, reply_markup=reply_markup)
    
    return PAYMENT_SUBMIT


async def payment_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm payment submission"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "payment_cancel":
        await query.edit_message_text("❌ تم إلغاء الدفع")
        return ConversationHandler.END
    
    user = query.from_user
    db = SessionLocal()
    
    try:
        tenant = get_tenant_by_owner(user.id)
        
        if not tenant:
            await query.edit_message_text("❌ خطأ: الصالون غير موجود")
            return ConversationHandler.END
        
        # Create payment record
        payment = PaymentManager.create_payment(
            db,
            tenant,
            context.user_data['amount'],
            context.user_data['plan'],
            context.user_data['payment_method'],
            context.user_data['transaction_id']
        )
        
        logger.info(
            f"Payment submitted: {payment.id} for tenant {tenant.tenant_id} "
            f"(${payment.amount})"
        )
        
        success_message = f"""
✅ تم استقبال الدفع!

📋 تفاصيل الدفع:
🆔 رقم المعاملة: `{payment.id}`
📱 رقم المحفظة: `{context.user_data['transaction_id']}`
💰 المبلغ: ${payment.amount}
📊 الخطة: {payment.plan.upper()}

⏳ سيتم مراجعة الدفع من قبل فريقنا
🔔 سيتم إبلاغك عند الموافقة

وقت الموافقة المتوقع: 1-2 ساعة
"""
        
        await query.edit_message_text(success_message, parse_mode="Markdown")
        
        # Notify admin
        admin_message = f"""
💳 دفع جديد بانت��ار الموافقة!

💼 الصالون: {tenant.salon_name}
📱 الملاك: {user.first_name} ({user.id})
💰 المبلغ: ${payment.amount}
📊 الخطة: {payment.plan.upper()}
🏦 الطريقة: {payment.payment_method.value}
🔑 رقم المعاملة: {payment.transaction_id}
🆔 معرف الدفع: {payment.id}

استخدم /admin للموافقة
"""
        
        if config.ADMIN_ID:
            try:
                await context.bot.send_message(
                    chat_id=config.ADMIN_ID,
                    text=admin_message
                )
            except Exception as e:
                logger.error(f"Failed to notify admin: {e}")
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        await query.edit_message_text(
            "❌ حدث خطأ أثناء معالجة الدفع. الرجاء المحاولة لاحقاً"
        )
        return ConversationHandler.END
    finally:
        db.close()


def get_payment_handler():
    """Get conversation handler for payment"""
    return ConversationHandler(
        entry_points=[CommandHandler("pay", start_payment)],
        states={
            PAYMENT_METHOD: [CallbackQueryHandler(payment_method_handler)],
            PAYMENT_PLAN: [CallbackQueryHandler(payment_plan_handler)],
            PAYMENT_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_details_handler)],
            PAYMENT_SUBMIT: [CallbackQueryHandler(payment_confirm_handler)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )
