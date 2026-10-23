# MandiCluster — Market & Price-Pattern Segmentation

An end-to-end machine learning project that groups Indian agricultural markets into price-based clusters, helping users explore similarities in reported commodity prices across markets.

## Overview

MandiCluster is a data-driven market segmentation application that analyzes agricultural market-price data and groups markets with similar price characteristics using **unsupervised machine learning**.

The system combines a React frontend, a FastAPI backend, a PostgreSQL database, and precomputed K-Means clustering results. Users can select a commodity, compare cluster-level prices, explore cluster characteristics, and search and filter individual markets.

The project focuses on understanding market-price groupings in the available dataset. It does not predict future commodity prices or determine which market will be the most profitable.

## Objectives

- Analyze agricultural market-price data for individual commodities.
- Group markets according to their price characteristics.
- Compare average modal prices across discovered clusters.
- Explore market-level results through an interactive dashboard.
- Store source observations and clustering results in PostgreSQL.
- Provide REST API endpoints to retrieve commodity, cluster, and market information.
- Build a complete full-stack machine learning application.

## Key Features

### Interactive Dashboard
- View market records and discovered clusters for a selected commodity.
- Display the mean modal price and silhouette score.
- Compare average modal prices using a bar chart.
- Explore cluster-level statistics.

### Market Exploration
- Search markets by market name, district, or state.
- Filter market records by cluster.
- View average modal price, price range, location, and cluster assignment.
- Navigate through market records using pagination.

### Machine Learning
- Apply K-Means clustering to group markets by price characteristics.
- Evaluate clustering quality using the silhouette score.
- Store cluster assignments and cluster profiles for supported commodities.
- Review clustering evaluation results to assess whether a result is promising or needs further review.

### Backend and Database
- Expose REST APIs through FastAPI.
- Store commodities, markets, price observations, clustering runs, and market-cluster assignments in PostgreSQL.
- Separate API routes, database models, schemas, and service logic.

## Technology Stack
---------------------------------------------------------
| Area               | Technologies                     |
|--------------------|----------------------------------|
| Frontend           | React, JavaScript, Vite          |
| UI and icons       | CSS, Lucide React                |
| Data visualization | Recharts                         |
| Backend            | Python, FastAPI                  |
| API server         | Uvicorn                          |
| Database           | PostgreSQL                       |
| Database access    | SQLAlchemy                       |
| Database driver    | Psycopg                          |
| Data processing    | Pandas                           |
| Machine learning   | Scikit-learn, K-Means clustering |
| Version control    | Git and GitHub                   |
---------------------------------------------------------

## System Architecture

```text
Agricultural Market-Price Dataset
              |
              v
     Data Processing
              |
              v
    Machine Learning
   K-Means Clustering
              |
              v
   Cluster Evaluation
              |
              v
      PostgreSQL
              |
              v
       FastAPI Backend
              |
          REST API
              |
              v
       React Frontend
              |
              v
   Interactive Dashboard
```

The clustering outputs are generated during the machine-learning workflow and imported into PostgreSQL. The dashboard retrieves the stored results through the backend API.

## Machine Learning Approach

MandiCluster uses unsupervised learning to identify groups of markets with similar price characteristics.

### Main processing stages

1. Load and inspect the agricultural market-price dataset.
2. Clean and prepare the required market and price fields.
3. Aggregate records to obtain market-level price features for individual commodities.
4. Evaluate candidate clustering configurations.
5. Apply K-Means clustering to suitable commodity datasets.
6. Evaluate cluster separation using the silhouette score.
7. Export cluster assignments, cluster profiles, and evaluation results.
8. Import the results into PostgreSQL for API access.

### Features used in clustering

The generated cluster-assignment output includes:

- Average modal price
- Minimum modal price
- Maximum modal price
- Average price range
- Observation count

The exact feature transformations and scaling used by the training pipeline should be reviewed in the machine-learning source code.

### Clustering evaluation

The silhouette score is used as a diagnostic to assess how well-separated the resulting clusters are. It is not a measure of market profitability or a guarantee that the clusters will generalize to future data.

## Dataset and Current Results

The project uses agricultural market-price data containing fields such as state, district, market, commodity, variety, grade, arrival date, minimum price, maximum price, and modal price.

The currently processed dataset contains:
|---------------------------------------------------------|
| Item                                   | Current result |
|----------------------------------------|----------------|
| Source records imported                | 19,213         |
| Distinct commodities in the database   | 284            |
| Markets in the database                | 2,050          |
| Stored market observations             | 19,213         |
| Commodities with clustering results    | 104            |
| Stored cluster assignments             | 16,460         |
| Clustered commodities marked promising | 42             |
| Clustered commodities needing review   | 62             |
|---------------------------------------------------------|
The source dataset currently represents a single observation date: **16 October 2026**. The clustering results therefore describe price groupings in that dataset, not historical price trends or changes over time.

The number of markets represented in a clustering result may differ from the number of source observations because the machine-learning pipeline aggregates and filters records.

## Getting Started

### Prerequisites

Install the following software before running the project:

- Python
- Node.js and npm
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd MandiCluster
```

Replace the placeholder with the URL of your GitHub repository.

### 2. Configure the Backend

Open a terminal in the project root and enter the backend directory:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows Git Bash:

```bash
python -m .venv/Scripts/activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure PostgreSQL

Create a PostgreSQL database named:

```text
mandicluster_db
```

Create `backend/.env` with your local database credentials:

```dotenv
DB_USER=postgres
DB_PASSWORD=YOUR_LOCAL_DATABASE_PASSWORD
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mandicluster_db
```

Replace the password placeholder with your local PostgreSQL password. Never commit this file or publish your database credentials.

### 4. Initialize and Import Data

From the `backend` directory, with the virtual environment activated, run the project's database scripts in the appropriate order:

```bash
python -m app.db.init_db
python -m app.db.update_observation_schema
python -m app.db.import_data
python -m app.db.import_clusters
```

These scripts initialize the database schema, apply the observation-schema update, import source data, and import the generated clustering results.

Run the imports only when needed. Follow the source code and existing database state before rerunning import scripts, particularly if you have already populated the database.

### 5. Start the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The local API is available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Configure the Frontend

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the JavaScript dependencies:

```bash
npm install
```

Create `frontend/.env.local`:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

This configures the local frontend to use the local FastAPI backend.

### 7. Start the Frontend

From the `frontend` directory:

```bash
npm run dev
```

Open the local URL printed by Vite in your browser.

Keep the backend and frontend terminals running while using the application.


## Configuration and Deployment

The frontend reads its backend URL from the `VITE_API_BASE_URL` environment variable. This allows the local project and deployed project to use different API addresses.

For online deployment:

1. Deploy the FastAPI backend to a suitable hosting service.
2. Provision a PostgreSQL database accessible to the backend.
3. Configure the backend's database environment variables securely.
4. Import the source data and clustering results into the deployed database.
5. Configure the deployed frontend with the backend's public API URL.
6. Rebuild and deploy the frontend.
7. Configure backend CORS to allow requests from the deployed frontend origin.

Do not use `localhost` as the API URL in a publicly deployed frontend. In a visitor's browser, `localhost` refers to that visitor's own device.

The frontend and backend must both be deployed, and the backend must be able to connect to its database, for the public application to work.

## Limitations

- The current dataset represents a single date and cannot establish historical price trends or price stability over time.
- Clustering identifies similarity in selected features; it does not establish causation, demand, profitability, or future prices.
- Only 104 commodities currently have stored clustering results, although 284 commodities exist in the database.
- Some commodity datasets may be unsuitable for reliable clustering and are excluded or marked for review by the existing pipeline.
- Silhouette scores are diagnostics and should be interpreted alongside cluster sizes, feature distributions, and data quality.
- Real-world decisions require current data, appropriate validation, and additional market context.

## Future Improvements

- Integrate regularly updated market-price data.
- Track price changes across multiple dates.
- Compare clustering results across different periods.
- Add more detailed model evaluation and cluster visualizations.
- Automate data ingestion and model retraining.
- Add deployment monitoring, logging, and automated tests.
- Improve data validation and document feature preprocessing.

## Learning Outcomes

This project brings together several practical areas of software development and machine learning:

- Data cleaning and feature engineering
- Unsupervised machine learning and model evaluation
- Python backend development with FastAPI
- Relational database design and PostgreSQL
- SQLAlchemy ORM and REST API integration
- React component architecture and state management
- Data visualization and interactive filtering
- Environment configuration and deployment preparation
- Git and GitHub version control

## License

Choose and add a license before distributing the project for reuse. Until a license is added, do not assume that others have permission to reuse or redistribute the code.

---

**MandiCluster — Market & Price-Pattern Segmentation**

*Exploring agricultural market-price similarities through data analysis and unsupervised machine learning.*
