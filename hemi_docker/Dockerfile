# Dockerfile for heminetwork

# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Install necessary packages (update, upgrade, and install required tools)
RUN apt-get update && apt-get install -y \
    vim \
    wget \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy your binary to the Docker container
# Assuming the binary (popmd) is in the same directory as the Dockerfile
COPY ./bin/popmd /usr/local/bin/popmd

# Set executable permissions for the binary
RUN chmod +x /usr/local/bin/popmd

# Set environment variables (can override with docker-compose)
ENV POPM_STATIC_FEE=250
ENV POPM_BFG_URL=wss://testnet.rpc.hemi.network/v1/ws/public

# Command to run the binary
CMD ["/usr/local/bin/popmd"]
