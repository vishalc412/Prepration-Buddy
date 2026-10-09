"""Django 5.2: demonstrate and repair N+1 using an actual SQLite ORM query count."""
from django.conf import settings
settings.configure(SECRET_KEY="offline-fixture",DEBUG=True,INSTALLED_APPS=[],
    DATABASES={"default":{"ENGINE":"django.db.backends.sqlite3","NAME":":memory:"}})
import django
django.setup()
from django.db import connection, models
from django.test.utils import CaptureQueriesContext

class Customer(models.Model):
    tenant = models.CharField(max_length=30)
    name = models.CharField(max_length=50)
    class Meta:
        app_label = "offline_queries"

class Ticket(models.Model):
    tenant = models.CharField(max_length=30)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    class Meta:
        app_label = "offline_queries"

def serialize(rows):
    return [{"id":row.pk,"subject":row.subject,"customer":row.customer.name} for row in rows]

def bounded_page(trusted_tenant, limit=50):
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ValueError("Limit outside 1..50")
    rows = Ticket.objects.filter(tenant=trusted_tenant,customer__tenant=trusted_tenant).select_related("customer").order_by("pk")[:limit]
    return serialize(rows)

def self_test():
    with connection.schema_editor() as schema:
        schema.create_model(Customer); schema.create_model(Ticket)
    acme = Customer.objects.create(tenant="acme",name="Acme Buyer")
    bravo = Customer.objects.create(tenant="bravo",name="Bravo Buyer")
    Ticket.objects.bulk_create([Ticket(tenant="acme",customer=acme,subject=f"issue-{n}") for n in range(50)])
    Ticket.objects.create(tenant="bravo",customer=bravo,subject="private")
    # Bad relation fixture: tenant field alone must not expose another tenant's customer.
    bad = Ticket.objects.create(tenant="acme",customer=bravo,subject="bad cross-tenant link")
    with CaptureQueriesContext(connection) as queries:
        slow = serialize(Ticket.objects.filter(tenant="acme").exclude(pk=bad.pk).order_by("pk"))
    slow_count = len(queries)
    assert slow_count == 51
    with CaptureQueriesContext(connection) as queries:
        fast = bounded_page("acme")
    assert len(queries) == 1 and slow == fast and len(fast) == 50
    assert all(row["customer"] == "Acme Buyer" for row in fast)
    assert len(bounded_page("bravo")) == 1
    for limit in [0,51,True]:
        try:
            bounded_page("acme",limit)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid pagination accepted")
    print(f"PASS: query budget {slow_count}->1, payload parity, bounded page, relation isolation")

if __name__ == "__main__":
    self_test()
