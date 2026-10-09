public final class PricePolicy {
    private PricePolicy() {}

    public static long total(int unitCents, int quantity) {
        if (unitCents < 0 || unitCents > 1_000_000) {
            throw new IllegalArgumentException("unit cents outside supported range");
        }
        if (quantity < 1 || quantity > 10_000) {
            throw new IllegalArgumentException("quantity outside supported range");
        }
        Integer boxed = new Integer(quantity);
        return Math.multiplyExact((long) unitCents, boxed.intValue());
    }
}
