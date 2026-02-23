# SOFE4630U – Milestone 4  
## Smart Meter & Voting System Microservices Architecture

This repository contains the complete implementation for Milestone 4.  
The project demonstrates a microservices-based architecture using:

- Google Kubernetes Engine (GKE)
- Google Cloud Pub/Sub
- Attribute-based filtered subscriptions
- BigQuery subscriptions
- Dockerized services
- Event-driven processing

---

# Project Overview

This milestone includes two major systems:

1. Voting System Microservices
2. Smart Meter Streaming Preprocessing (Microservices replacement for Dataflow)

Both systems are implemented using containerized microservices deployed to GKE.

---

# Part 1 – Voting System Microservices

The voting system consists of the following microservices:

- `voting_machine` – Publishes vote messages to Pub/Sub
- `voting_record` – Stores votes in PostgreSQL
- `voting_logger` – Logs election results
- `redis` – Caching layer
- `postgres` – Database for vote storage

## Technologies Used

- Python
- Docker
- Kubernetes Deployments
- Pub/Sub messaging
- PostgreSQL
- Redis

---

# Part 2 – Smart Meter Preprocessing (Microservices Architecture)

This design replaces a centralized Dataflow pipeline with an event-driven microservices architecture.

## Architecture Overview

- One main Pub/Sub topic: `smart-meter`
- Multiple filtered subscriptions
- Independent processing microservices
- BigQuery subscription for automatic storage

Message flow:

`raw → validated → processed`

---

# Smart Meter Microservices

## 1. FilterReading Service

Directory: `smart_meter_filter`

### Responsibility
- Subscribes to messages where `stage="raw"`
- Validates measurement fields
- Drops records containing null values
- Republishes valid records with `stage="validated"`

### Purpose
Prevents incomplete or corrupted data from continuing through the pipeline.

---

## 2. ConvertReading Service

Directory: `smart_meter_convert`

### Responsibility
- Subscribes to messages where `stage="validated"`
- Converts:
  - Temperature (°C → °F)
  - Pressure (kPa → PSI)
- Republishes enriched message with `stage="processed"`

### Conversion Formulas

- Temperature:  
  `TF = TC × 1.8 + 32`

- Pressure:  
  `Ppsi = PkPa ÷ 6.895`

---

## 3. BigQuery Subscription

- Subscribes to `stage="processed"` messages
- Automatically inserts processed records into BigQuery
- No additional storage microservice required

BigQuery Dataset:
- `smart_meter_ds`

Tables:
- `pubsub_ingest`
- `readings`

---

# Deployment

All services are:

- Dockerized
- Built using Cloud Build
- Stored in Artifact Registry
- Deployed to GKE using Kubernetes manifests

Kubernetes resources include:

- Deployments
- Service Accounts
- Workload Identity configuration
- Environment variable configuration

---

# Key Cloud Features Demonstrated

- Pub/Sub attribute-based filtering
- Event-driven microservices
- Workload Identity (secure GCP access from GKE)
- BigQuery direct subscription integration
- Container image build and push via Cloud Build
- GKE rollout and deployment management

---

# Learning Outcomes Demonstrated

- Microservices architecture design
- Streaming data validation and transformation
- Loose coupling using Pub/Sub
- Cloud-native application deployment
- Kubernetes troubleshooting and rollout management
- Replacement of centralized processing (Dataflow) with modular services

---

# Author

Iqra Zahid  
SOFE4630U – Cloud & Distributed Systems  
Ontario Tech University

---
