#!/usr/bin/env python3
"""
Main application entry point for local development
"""
from webApp import app

if __name__ == '__main__':
    # Run in debug mode for local development
    app.run(debug=True, host='0.0.0.0', port=5000)
