# syntax=docker/dockerfile:1
FROM ubuntu:focal AS builder
WORKDIR /workspaces/

RUN apt-get update -y && apt-get upgrade -y &&  \
    apt-get install wget curl -y && mkdir -p /workspaces && \
    cd /workspaces && \
    chmod +x *.sh && \
    echo "Building." && \
    ./entrypoint.sh "--build"


FROM alpine:latest  
RUN apk --no-cache add ca-certificates

RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser
USER appuser

WORKDIR /workspaces2/
COPY --from=builder /workspaces/ ./
CMD ["./entrypoint.sh"]