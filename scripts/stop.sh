#!/bin/bash

echo "[STOP] Shutting down bot..."
pm2 stop modmeister-bot 2>/dev/null || echo "[STOP] Bot not running or PM2 unavailable"
echo "[STOP] Complete"