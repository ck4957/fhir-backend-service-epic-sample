#!/bin/bash
#
# RevStream Setup Script
# Sets up the complete RevStream Integration Pipeline environment
#

set -e

echo "=============================================="
echo "  RevStream Integration Pipeline Setup"
echo "=============================================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "✓ Docker is installed"
echo ""

# Create required directories
echo "Creating directories..."
mkdir -p iris-data
mkdir -p billing-simulator/received
mkdir -p errors

echo "✓ Directories created"
echo ""

# Build and start containers
echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting containers..."
docker-compose up -d

echo ""
echo "Waiting for IRIS to initialize (this may take 2-3 minutes)..."
sleep 30

# Check if IRIS is ready
MAX_ATTEMPTS=20
ATTEMPT=1
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:52773/csp/sys/UtilHome.csp > /dev/null 2>&1; then
        echo "✓ IRIS is ready!"
        break
    fi
    echo "  Waiting for IRIS... (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 10
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    echo "WARNING: IRIS may not be fully ready. Check logs with: docker-compose logs iris"
fi

echo ""
echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "Access Points:"
echo "  - IRIS Management Portal: http://localhost:52773/csp/sys/UtilHome.csp"
echo "    Username: SuperUser"
echo "    Password: SYS (change on first login)"
echo ""
echo "  - HL7 Inbound Port: localhost:7021"
echo "  - Billing Simulator: localhost:7022"
echo ""
echo "Next Steps:"
echo "  1. Open IRIS Management Portal"
echo "  2. Navigate to Interoperability > Configure > Production"
echo "  3. Import the RevStream Production classes"
echo "  4. Start the production"
echo "  5. Send test HL7 messages using: ./scripts/send-test-message.sh"
echo ""
echo "Useful Commands:"
echo "  - View logs:        docker-compose logs -f"
echo "  - Stop services:    docker-compose down"
echo "  - Restart services: docker-compose restart"
echo ""
