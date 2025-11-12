# ===== Build Stage =====
FROM maven:3.9.4-eclipse-temurin-21 AS build
WORKDIR /workspace/app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

# ===== Run Stage =====
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /workspace/app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]
