# Java Maven Sample Application

See [prerequisites](https://paketo.io/docs/howto/java/#prerequisites) of this sample.

## Building

```bash
pack build applications/maven
```

Alternatively, if you want to attach a Maven `settings.xml` file to pass additional configuration to Maven.

```bash
pack build applications/maven --env BP_JVM_VERSION=17 --volume $(pwd)/bindings:/platform/bindings
```

The command above will use the sample `settings.xml` file from this repo. It may be more useful to copy your local `settings.xml` first.

```bash
cp ~/.m2/settings.xml java/maven/bindings/maven/settings.xml
pack build applications/maven --volume $(pwd)/bindings:/platform/bindings
```

## Running

```bash
docker run --rm --tty --publish 8080:8080 applications/maven
```

## Viewing

```bash
curl -s http://localhost:8080/actuator/health | jq .
```
