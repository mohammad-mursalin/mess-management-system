from decimal import Decimal

from apps.members.models import Member
from .models import GroceryBillItem


def member_choices_json(cycle):
    if cycle is None:
        return []
    members = Member.objects.filter(
        is_active=True,
        cycles__cycle=cycle,
    ).distinct().order_by('name')
    return [{'id': m.id, 'name': m.name} for m in members]


def to_decimal(raw, default=Decimal('0')):
    try:
        if raw is None or str(raw).strip() == '':
            return default
        return Decimal(str(raw))
    except Exception:
        return default


def sync_bill_items(bill, post):
    item_names = post.getlist('item_name')
    quantities = post.getlist('quantity')
    unit_prices = post.getlist('unit_price')

    paired = []
    for i in range(len(item_names)):
        name = item_names[i].strip() if i < len(item_names) else ''
        if not name:
            continue
        qty = to_decimal(quantities[i] if i < len(quantities) else '')
        price = to_decimal(unit_prices[i] if i < len(unit_prices) else '')
        paired.append((name, qty, price))

    existing_ids = list(
        bill.items.order_by('id').values_list('id', flat=True)
    )

    for i, (name, qty, price) in enumerate(paired):
        if i < len(existing_ids):
            item = GroceryBillItem.objects.get(pk=existing_ids[i])
            item.item_name = name
            item.quantity = qty
            item.unit_price = price
            item.save()
        else:
            GroceryBillItem.objects.create(
                grocery_bill=bill, item_name=name, quantity=qty, unit_price=price
            )

    if len(paired) < len(existing_ids):
        GroceryBillItem.objects.filter(
            grocery_bill=bill, id__in=existing_ids[len(paired):]
        ).delete()
