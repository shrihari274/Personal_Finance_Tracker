Threat-Aware DevSecOps Pipeline for a Web Application

1. Introduction

This project demonstrates a complete, end-to-end DevSecOps pipeline that automates the build, security validation, deployment, and monitoring of a containerized Python Flask application. It serves as a practical blueprint for integrating security into every phase of the software development lifecycle (SDLC), proving that development velocity and robust security can be achieved concurrently.

The core principle is to "Shift Left," embedding security from the initial design phase through automated gates in the CI/CD pipeline, and "Shift Right," by continuously monitoring the application in its runtime environment.


2. Key Features

- Proactive Security Design: Utilizes the STRIDE framework for threat modeling to identify and mitigate risks before development.

- Automated CI/CD Pipeline: A fully automated workflow orchestrated by Jenkins that triggers   on every code commit.

- Automated Security Gates: Integrates ThreatMapper to perform vulnerability, secret, and     malware scanning on every build, automatically blocking insecure deployments.

- Secure Containerization: A hardened Docker image built on security best practices, including minimal base images and non-root users.

- Runtime Threat Detection: Continuous monitoring of the live application container using the ThreatMapper sensor to detect runtime threats and map attack paths.

- Host Security Auditing: Periodic infrastructure audits using Docker Bench for Security to ensure compliance with CIS benchmarks.

- Centralized SIEM: All pipeline, application, and security logs are aggregated into Splunk for unified visibility, real-time monitoring, and correlated alerting.

3. Architecture

<img width="5091" height="1286" alt="diagram-export-8-4-2025-3_18_50-PM" src="https://github.com/user-attachments/assets/f0897fac-db81-472e-a7b1-c9625e300de7" />

4.Technology Stack

<img width="496" height="393" alt="TS" src="https://github.com/user-attachments/assets/9aaa85be-6d2e-43a8-b634-d56dcc14ee3a" />


