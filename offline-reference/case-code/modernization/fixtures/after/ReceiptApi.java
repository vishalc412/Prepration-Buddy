public final class ReceiptApi {
    private final InvoiceService service = new InvoiceService();

    public String receipt(String tenant, int unitCents, int quantity) {
        if (tenant == null || !tenant.matches("[a-z][a-z0-9-]{0,31}")) {
            throw new IllegalArgumentException("invalid tenant identifier");
        }
        return tenant + ":" + service.invoice(unitCents, quantity);
    }
}
