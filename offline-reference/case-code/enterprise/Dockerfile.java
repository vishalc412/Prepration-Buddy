# Authored deployment exercise; not built or deployed by this case's test.
FROM maven:3.9.9-eclipse-temurin-17 AS build
WORKDIR /source
COPY pom.xml EnterpriseGateway.java ./
RUN mvn -q compile org.apache.maven.plugins:maven-dependency-plugin:3.7.0:copy-dependencies -DoutputDirectory=runtime-libs
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /source/target/classes ./classes
COPY --from=build /source/runtime-libs ./lib
USER 10001:10001
CMD ["java", "-cp", "/app/classes:/app/lib/*", "bootcampcase.EnterpriseGateway", "--server.port=8080", "--server.address=0.0.0.0"]
