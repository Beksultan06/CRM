from django.utils.timezone import localdate
from django.db.models import Sum
from app.manager.models import Payment

def today_summary():
    today = localdate()
    payments = Payment.objects.filter(date=today)
    agg = payments.aggregate(
        total=Sum("total_amount"),
        cash=Sum("amount_cash"),
        transfer=Sum("amount_transfer"),
        online=Sum("amount_online")
    )
    return {
        "total": agg["total"] or 0,
        "cash": agg["cash"] or 0,
        "transfer": agg["transfer"] or 0,
        "online": agg["online"] or 0
    }
