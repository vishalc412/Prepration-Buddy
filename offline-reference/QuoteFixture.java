public final class QuoteFixture {
    public static String quote(String value) {
        if (value == null) throw new IllegalArgumentException("value required");
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }
    public static void main(String[] args) {
        check("\"hello\"", quote("hello"));
        check("\"a\\\"b\"", quote("a\"b"));
        check("\"a\\\\b\"", quote("a\\b"));
        check("\"\"", quote(""));
        try { quote(null); throw new AssertionError("null accepted"); }
        catch (IllegalArgumentException expected) {
            check("value required", expected.getMessage());
        }
        System.out.println("PASS 5 Java behavior cases");
    }
    private static void check(String expected, String actual) {
        if (!expected.equals(actual)) throw new AssertionError(expected + " != " + actual);
    }
}
