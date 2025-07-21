#!/bin/bash

# Run all Streamlit applications on different ports
streamlit run app.py --server.port=8501 &
streamlit run app2.py --server.port=8502 &
streamlit run app3.py --server.port=8503 &

# Wait to keep the container alive
wait
