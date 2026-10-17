FROM eclipse-temurin:17-jdk-jammy
WORKDIR /app
COPY . .
RUN ./mvnw clean package -DskipTests
EXPOSE 8080
CMD ["java", "-jar", "target/*.jar"]
