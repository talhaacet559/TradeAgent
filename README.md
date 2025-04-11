# TradeAgent
Project Overview

The system is built using a microservice architecture with two instances, designed to handle data from Binance for BTC/USDT trading pairs. It leverages Redis for caching, Kafka for streaming signals and Mongo for db service. Key
points for project go as below:

    WebSocket & Klines Data:
    
    The system retrieves WebSocket and Klines data from Binance.
    
    Signal Generation:
    
    Using a Simple Moving Average (SMA) algorithm, the EntityService analyzes the data, makes a trading decision, and sends the signal back to be logged into the database within the EntityService.

    Prometheus Metrics:
    
    Prometheus scrapes metrics from both services to monitor performance and track various statistics.

Room for improvement:
    
    Trade Execution:
    
    The ClientService can optionally use the generated signals to place trades inside clientservices (Not implemented.)

    Testing:

    The system could have been tested by integrating with Redis, Kafka, MongoDB, and Binance API endpoints to ensure proper integration.
    Additionally, unit tests could have been written for the background agents within the services to verify their functionality.
    
    Health Endpoints:
    
    Health check endpoints could have been planned to report on the status of background agents, including WebSocket connections, database interactions, and external API availability.

Challenges

    Time Constraints: Managed to meet deadline while trying to figure out external APIs and manage data structures.
    
    MongoDB Integration: MongoDB, using for the first time.
    
    Docker containers: Implemented wait-for script.
    
    Unstable Binance WebSocket endpoints:  Implemented retry mechanism and restart endpoint.

Author: Ömer Talha Acet