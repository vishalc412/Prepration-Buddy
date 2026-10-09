"""Django 5.2 atomic order + outbox fixture. No message broker or external effect."""
import hashlib
import json
from django.conf import settings
settings.configure(SECRET_KEY="offline-fixture", INSTALLED_APPS=[],
    DATABASES={"default":{"ENGINE":"django.db.backends.sqlite3","NAME":":memory:"}})
import django
django.setup()
from django.db import IntegrityError, connection, models, transaction

class Order(models.Model):
    tenant = models.CharField(max_length=30)
    request_key = models.CharField(max_length=80)
    digest = models.CharField(max_length=64)
    quantity = models.IntegerField()
    class Meta:
        app_label = "offline_outbox"
        constraints = [models.UniqueConstraint(fields=["tenant","request_key"],name="tenant_request_unique"),
                       models.CheckConstraint(condition=models.Q(quantity__gt=0),name="positive_quantity")]

class Outbox(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE)
    payload = models.TextField()
    sent = models.BooleanField(default=False)
    class Meta:
        app_label = "offline_outbox"

def place_order(trusted_tenant, key, quantity, wakeups, fail_after_write=False):
    # trusted_tenant comes from verified server identity, not a request tenant field.
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("Quantity must be a positive integer")
    digest = hashlib.sha256(json.dumps({"quantity":quantity},sort_keys=True).encode()).hexdigest()
    with transaction.atomic():
        existing = Order.objects.filter(tenant=trusted_tenant,request_key=key).first()
        if existing:
            if existing.digest != digest:
                raise ValueError("Idempotency conflict")
            return existing.pk
        order = Order.objects.create(tenant=trusted_tenant,request_key=key,digest=digest,quantity=quantity)
        Outbox.objects.create(order=order,payload=json.dumps({"order_id":order.pk,"quantity":quantity}))
        # Wakeup is advisory. A periodic dispatcher must scan durable unsent rows.
        transaction.on_commit(lambda: wakeups.append(order.pk))
        if fail_after_write:
            raise RuntimeError("Injected crash before commit")
        return order.pk

def dispatch_fixture():
    # Only local status simulation; real consumers deduplicate by event/order ID.
    return Outbox.objects.filter(sent=False).update(sent=True)

def self_test():
    with connection.schema_editor() as schema:
        schema.create_model(Order); schema.create_model(Outbox)
    wakeups = []
    try:
        place_order("acme","rollback",3,wakeups,fail_after_write=True)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Injected failure did not raise")
    assert Order.objects.count() == Outbox.objects.count() == 0 and wakeups == []
    order_id = place_order("acme","buy-1",3,wakeups)
    assert wakeups == [order_id] and Outbox.objects.count() == 1
    assert place_order("acme","buy-1",3,wakeups) == order_id
    try:
        place_order("acme","buy-1",4,wakeups)
    except ValueError:
        pass
    else:
        raise AssertionError("Conflicting replay accepted")
    for kwargs in [dict(tenant="acme",request_key="buy-1",quantity=3),dict(tenant="acme",request_key="bad",quantity=-1)]:
        try:
            with transaction.atomic():
                Order.objects.create(digest="x",**kwargs)
        except IntegrityError:
            pass
        else:
            raise AssertionError("Database constraint failed")
    assert dispatch_fixture() == 1 and dispatch_fixture() == 0
    assert Order.objects.count() == Outbox.objects.count() == 1
    print("PASS: rollback, commit callback, transaction-committed outbox, unique/check constraints; no restart proof")

if __name__ == "__main__":
    self_test()
