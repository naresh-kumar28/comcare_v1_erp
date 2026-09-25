from django.db.models import Q
from apps.cart.models import UserAddress
from apps.accounts.models import CustomUser

unlinked = UserAddress.objects.filter(user__isnull=True)
synced_count = 0

for addr in unlinked:
    email_val = (addr.email or '').strip()
    phone_val = (addr.phone or '').strip()
    matched_user = None
    if email_val:
        matched_user = CustomUser.objects.filter(email__iexact=email_val).first()
    if not matched_user and phone_val:
        q = Q(phone_number=phone_val)
        if phone_val.startswith('+91'):
            q |= Q(phone_number=phone_val[3:])
        elif len(phone_val) == 10:
            q |= Q(phone_number='+91' + phone_val)
        matched_user = CustomUser.objects.filter(q).first()

    if matched_user:
        addr.user = matched_user
        addr.session_key = None
        addr.save()
        synced_count += 1
        print(f"Successfully linked Address ID {addr.id} ({addr.full_name}) -> User ID {matched_user.id} ({matched_user.email})")

print(f"DONE. Total Addresses Synced: {synced_count}")
