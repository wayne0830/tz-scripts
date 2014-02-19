mvn deploy:deploy-file \
    -DgroupId=com.travelzen \
    -DartifactId=tops-flight-thrift \
    -Dversion=1.0-SNAPSHOT \
    -Dpackaging=jar \
    -Durl=http://192.168.160.187:8081/nexus/content/repositories/snapshots/ \
    -DrepositoryId=snapshots
    -Dfile=/tmp/tops-flight-thrift-1.0-SNAPSHOT.jar
