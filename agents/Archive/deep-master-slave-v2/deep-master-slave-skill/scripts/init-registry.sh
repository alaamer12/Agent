#!/bin/bash
# Initialize the agents/ registry with core agent identities

REGISTRY_DIR="agents"
mkdir -p "$REGISTRY_DIR"

# Copy agent files from skill
cp ../agents/*.md "$REGISTRY_DIR/" 2>/dev/null || echo "No agent files found in ../agents/"

echo "✅ Agent registry initialized at $REGISTRY_DIR/"
echo "   Agents available:"
ls -1 "$REGISTRY_DIR/" | sed 's/^/   - /'
