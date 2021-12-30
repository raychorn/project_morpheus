# syntax=docker/dockerfile:1
FROM ubuntu:focal AS builder
WORKDIR /workspaces/

RUN apt-get update -y && apt-get upgrade -y &&  \
    apt-get install wget curl -y && mkdir -p /workspaces && \
    cd /workspaces && \
    curl -L "https://vypercdn1.s3.us-east-2.amazonaws.com/project_morpheus.tgz" -o morpheus.tar.gz && \
    echo "Sleeping 10 secs" && sleep 10 && \
    tar -xvzf "morpheus.tar.gz" && \
    chmod +x *.sh && \
    echo "Starting." && \
    ./entrypoint.sh "--build"


FROM alpine:latest  
RUN apk --no-cache add ca-certificates
USER appuser
WORKDIR /workspaces2/
COPY --from=builder /workspaces/ ./
CMD ["./entrypoint.sh"]