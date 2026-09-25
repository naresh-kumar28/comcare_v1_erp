from django.db.models import Q
from apps.cart.models import UserAddress
from apps.accounts.models import CustomUser

unlinked = UserAddress.objects.filter(user__isnull=True)
print(f"TOTAL UNLINKED ADDRESSES IN DB: {unlinked.count()}")

plan = []
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
        plan.append((addr, matched_user))

print(f"AFFECTED ADDRESSES COUNT TO SYNC: {len(plan)}")
for addr, user in plan:
    print(f"  -> Address ID {addr.id} ({addr.full_name} | Email: '{addr.email}' | Phone: '{addr.phone}') => Links to User ID {user.id} ({user.email})")
