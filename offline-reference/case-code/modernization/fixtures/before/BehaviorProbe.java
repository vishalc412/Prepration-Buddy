public final class BehaviorProbe {
    private static int checked = 0;

    private static void equal(long actual, long expected) {
        checked++;
        if (actual != expected) throw new AssertionError(actual + " != " + expected);
    }

    private static void text(String actual, String expected) {
        checked++;
        if (!actual.equals(expected)) throw new AssertionError(actual + " != " + expected);
    }

    private static void rejects(Runnable action) {
        checked++;
        try {
            action.run();
        } catch (IllegalArgumentException expected) {
            return;
        }
        throw new AssertionError("expected domain rejection");
    }

    public static void main(String[] args) {
        InvoiceService invoices = new InvoiceService();
        ReceiptApi api = new ReceiptApi();
        equal(invoices.invoice(0, 1), 0);
        equal(invoices.invoice(1250, 3), 3750);
        equal(invoices.invoice(1_000_000, 10_000), 10_000_000_000L);
        for (int unit : new int[] {0, 1, 99, 1250, 1_000_000}) {
            for (int quantity : new int[] {1, 2, 127, 128, 9999, 10_000}) {
                equal(invoices.invoice(unit, quantity), (long) unit * quantity);
            }
        }
        text(api.receipt("tenant-a", 1250, 3), "tenant-a:3750");
        text(api.receipt("tenant-b", 1250, 3), "tenant-b:3750");
        rejects(() -> invoices.invoice(-1, 1));
        rejects(() -> invoices.invoice(1_000_001, 1));
        rejects(() -> invoices.invoice(1, 0));
        rejects(() -> invoices.invoice(1, -1));
        rejects(() -> invoices.invoice(1, 10_001));
        rejects(() -> api.receipt(null, 1, 1));
        rejects(() -> api.receipt("../tenant", 1, 1));
        rejects(() -> api.receipt("Tenant-A", 1, 1));
        // The same externally observed signature must result before and after.
        System.out.println("{\"status\":\"PASS\",\"checks\":" + checked
            + ",\"receiptA\":\"" + api.receipt("tenant-a", 1250, 3)
            + "\",\"maxTotal\":" + invoices.invoice(1_000_000, 10_000) + "}");
    }
}
