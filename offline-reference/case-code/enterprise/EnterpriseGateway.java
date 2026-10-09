package bootcampcase;
import java.io.InputStream;
import java.net.URI;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;
import com.fasterxml.jackson.databind.*;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.*;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@SpringBootApplication
@RestController
public class EnterpriseGateway {
    // Trusted fixed principals are fixtures, not production authentication.
    private static final Map<String,String> ROLES=Map.of("Bearer token-acme-editor","editor","Bearer token-acme-viewer","viewer","Bearer token-bravo-editor","editor");
    private static final int MAX_BODY=16384, MAX_RESPONSE=65536;
    private final HttpClient client=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();
    private final ObjectMapper json=new ObjectMapper();
    private final URI pythonBase;
    public EnterpriseGateway() {
        pythonBase=URI.create(System.getenv().getOrDefault("PYTHON_BASE","http://127.0.0.1:9091"));
        if (!"http".equals(pythonBase.getScheme()) || !"127.0.0.1".equals(pythonBase.getHost()) || pythonBase.getPort()<1 || pythonBase.getUserInfo()!=null || pythonBase.getRawQuery()!=null || pythonBase.getRawFragment()!=null || !(pythonBase.getPath().isEmpty() || pythonBase.getPath().equals("/"))) throw new IllegalArgumentException("explicit loopback origin required");
    }
    @GetMapping("/health") public Map<String,String> health(){return Map.of("status","ready","implementation","Spring Boot");}
    private ResponseEntity<byte[]> error(int status,String message){return ResponseEntity.status(status).header("Content-Type","application/json").body(("{\"detail\":\""+message+"\"}").getBytes(StandardCharsets.UTF_8));}
    @PostMapping({"/api/assist","/api/tickets"})
    public ResponseEntity<byte[]> bridge(HttpServletRequest request) {
        String auth=request.getHeader("Authorization");
        String role=ROLES.get(auth==null?"":auth);
        if(role==null)return error(401,"verified demo principal required");
        boolean write=request.getRequestURI().equals("/api/tickets");
        if(write && !role.equals("editor"))return error(403,"editor role required");
        String type=request.getContentType();
        if(type==null || !type.split(";",2)[0].trim().equalsIgnoreCase("application/json"))return error(415,"application/json required");
        try {
            byte[] body;
            try(InputStream in=request.getInputStream()){body=in.readNBytes(MAX_BODY+1);}
            if(body.length>MAX_BODY)return error(413,"request body limit");
            HttpRequest.Builder outgoing=HttpRequest.newBuilder(pythonBase.resolve(write?"/tickets":"/assist")).timeout(Duration.ofSeconds(4)).header("Content-Type","application/json").header("Authorization",auth).POST(HttpRequest.BodyPublishers.ofByteArray(body));
            String key=request.getHeader("Idempotency-Key");if(key!=null)outgoing.header("Idempotency-Key",key);
            // Caller X-Tenant never becomes authoritative or forwarded.
            HttpResponse<InputStream> upstream=client.send(outgoing.build(),HttpResponse.BodyHandlers.ofInputStream());
            byte[] bytes;
            try(InputStream in=upstream.body()){bytes=in.readNBytes(MAX_RESPONSE+1);}
            if(bytes.length>MAX_RESPONSE)return error(502,"upstream response limit");
            JsonNode parsed=json.readTree(bytes);
            if(parsed==null || !parsed.isObject())return error(502,"invalid upstream envelope");
            return ResponseEntity.status(upstream.statusCode()).header("Content-Type","application/json").body(bytes);
        } catch(InterruptedException interrupted){Thread.currentThread().interrupt();return error(503,"bridge interrupted");}
        catch(Exception unavailable){return error(502,"upstream unavailable or invalid");}
    }
    @GetMapping("/api/tickets/{ticketId}")
    public ResponseEntity<byte[]> readTicket(@PathVariable String ticketId,HttpServletRequest request) {
        String auth=request.getHeader("Authorization");
        if(!ROLES.containsKey(auth==null?"":auth))return error(401,"verified demo principal required");
        if(!ticketId.matches("[a-f0-9]{32}"))return error(404,"ticket not found");
        try {
            HttpRequest outgoing=HttpRequest.newBuilder(pythonBase.resolve("/tickets/"+ticketId)).timeout(Duration.ofSeconds(4)).header("Authorization",auth).GET().build();
            HttpResponse<InputStream> upstream=client.send(outgoing,HttpResponse.BodyHandlers.ofInputStream());
            byte[] bytes;
            try(InputStream in=upstream.body()){bytes=in.readNBytes(MAX_RESPONSE+1);}
            if(bytes.length>MAX_RESPONSE)return error(502,"upstream response limit");
            JsonNode parsed=json.readTree(bytes);
            if(parsed==null || !parsed.isObject())return error(502,"invalid upstream envelope");
            return ResponseEntity.status(upstream.statusCode()).header("Content-Type","application/json").body(bytes);
        }catch(InterruptedException interrupted){Thread.currentThread().interrupt();return error(503,"bridge interrupted");}
        catch(Exception unavailable){return error(502,"upstream unavailable or invalid");}
    }
    public static void main(String[] args){SpringApplication.run(EnterpriseGateway.class,args);}
}
