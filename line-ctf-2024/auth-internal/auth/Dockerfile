FROM golang:latest

ENV GO111MODULE=on \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

COPY ./src /auth

WORKDIR /auth

RUN go mod download
RUN go build -o main .
RUN groupadd -r auth && useradd auth -g auth && mkdir /home/auth && chown -R auth:auth /home/auth && chown auth:auth /auth

USER auth

ENTRYPOINT ["/auth/main"]