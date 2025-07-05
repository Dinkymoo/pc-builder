#!/bin/bash
# Start the frontend using the AWS Lambda backend

cd "$(dirname "$0")"
cd pc-builder/pc-builder-app

echo "🚀 Starting Angular frontend with AWS Lambda backend..."
echo "📊 API URL: $(grep apiUrl src/environments/environment.ts | cut -d "'" -f 2)"

# Start Angular dev server
npm start
