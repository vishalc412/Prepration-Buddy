"""Django 5.2; standalone in-memory ORM + test client exercise.
Fixed credentials are trusted fixtures, not production identity verification.
"""
import json
from django.conf import settings
settings.configure(SECRET_KEY="offline-fixture-not-production", DEBUG=False,
    ALLOWED_HOSTS=["testserver"], ROOT_URLCONF=__name__, MIDDLEWARE=[],
    INSTALLED_APPS=[], DATABASES={"default":{"ENGINE":"django.db.backends.sqlite3","NAME":":memory:"}})
import django
django.setup()
from django.db import connection, models
from django.http import JsonResponse
from django.test import Client
from django.urls import path

class Invoice(models.Model):
    tenant = models.CharField(max_length=30)
    amount_cents = models.IntegerField()
    class Meta:
        app_label = "offline_tenant"

PRINCIPALS = {"Bearer fixture-acme-reader": ("acme","reader"),
              "Bearer fixture-acme-editor": ("acme","editor"),
              "Bearer fixture-bravo-editor": ("bravo","editor")}

def invoice_view(request, invoice_id):
    principal = PRINCIPALS.get(request.headers.get("Authorization"))
    if principal is None:
        return JsonResponse({"error":"unauthorized"}, status=401)
    tenant, role = principal
    # Tenant predicate belongs in every object lookup, before serialization/update.
    row = Invoice.objects.filter(tenant=tenant, pk=invoice_id).first()
    if row is None:
        return JsonResponse({"error":"not found"}, status=404)
    if request.method == "GET":
        return JsonResponse({"id":row.pk,"amount_cents":row.amount_cents})
    if request.method != "PATCH":
        return JsonResponse({"error":"method not allowed"}, status=405)
    if role != "editor":
        return JsonResponse({"error":"forbidden"}, status=403)
    try:
        body = json.loads(request.body)
        if not isinstance(body,dict) or set(body) != {"amount_cents"}:
            raise ValueError("Unexpected fields")
        amount = body["amount_cents"]
        if type(amount) is not int or not 0 <= amount <= 1_000_000:
            raise ValueError("Invalid amount")
    except (ValueError, TypeError, KeyError):
        return JsonResponse({"error":"invalid request"}, status=400)
    Invoice.objects.filter(pk=row.pk,tenant=tenant).update(amount_cents=amount)
    return JsonResponse({"id":row.pk,"amount_cents":amount})

urlpatterns = [path("invoices/<int:invoice_id>", invoice_view)]

def self_test():
    with connection.schema_editor() as schema:
        schema.create_model(Invoice)
    acme = Invoice.objects.create(tenant="acme",amount_cents=100)
    bravo = Invoice.objects.create(tenant="bravo",amount_cents=900)
    client = Client()
    reader = {"HTTP_AUTHORIZATION":"Bearer fixture-acme-reader", "HTTP_X_TENANT":"bravo"}
    editor = {"HTTP_AUTHORIZATION":"Bearer fixture-acme-editor"}
    assert client.get(f"/invoices/{acme.pk}", **reader).json()["amount_cents"] == 100
    assert client.get(f"/invoices/{bravo.pk}", **reader).status_code == 404
    assert client.get(f"/invoices/{acme.pk}").status_code == 401
    assert client.patch(f"/invoices/{acme.pk}",data=json.dumps({"amount_cents":5}),content_type="application/json",**reader).status_code == 403
    for body in [{"amount_cents":True},{"amount_cents":-1},{"amount_cents":5,"tenant":"bravo"}]:
        assert client.patch(f"/invoices/{acme.pk}",data=json.dumps(body),content_type="application/json",**editor).status_code == 400
    assert client.patch(f"/invoices/{acme.pk}",data=json.dumps({"amount_cents":250}),content_type="application/json",**editor).status_code == 200
    acme.refresh_from_db(); bravo.refresh_from_db()
    assert acme.amount_cents == 250 and bravo.amount_cents == 900
    print("PASS: tenant-scoped ORM reads/writes, role permission, validation")

if __name__ == "__main__":
    self_test()
