public final class InvoiceService {
    public long invoice(int unitCents, int quantity) {
        return PricePolicy.total(unitCents, quantity);
    }
}
