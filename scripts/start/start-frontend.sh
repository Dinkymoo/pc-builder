#!/bin/bash
# Run Angular frontend from project root
cd pc-builder/pc-builder-app || exit 1
npm install
npm start

{
  "/graphic-cards": {
    "target": "https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod",
    "secure": true,
    "changeOrigin": true,
    "logLevel": "debug"
  }
}
