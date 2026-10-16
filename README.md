# SQL Data Analyst Agent



An AI-powered analytics application that converts natural-language questions into SQL queries, executes them against a PostgreSQL database and presents the results through interactive tables, charts and AI-generated summaries.



Ask questions about your data in plain English instead of writing SQL manually.





## Database Schema



The application uses an e-commerce analytics database with five primary tables.



| Table | Description |
| ------ | ---------- |
| `customers` | Customer details, countries, and registration dates |
| `products` | Product names, categories, and prices |
| `orders` | Customer orders, dates, statuses, and total amounts |
| `order_items` | Products and quantities associated with each order |
| `payments` | Payment methods, amounts, and payment statuses |


The tables belong to the `analytics` schema.



## Example Questions

You can ask questions such as:

- How many customers are there in each country?
- What is the average order value?
- Which are the top 10 products by sales revenue?
- Show monthly revenue over time.
- Which customers have never placed an order?
- Which payment method has the highest failure rate?
- Find the top three products by revenue within each category.
- Which customers have spent more than the average customer spending?

The agent generates SQL, validates it, executes it against the database and returns the results with an explanation and a chart (if required).


## How to run

### Prerequisites

Install or configure the following:

- Python 3.11 or a compatible Python version
- Node.js and pnpm
- A Supabase PostgreSQL database
- An OpenRouter API key




### Configure the backend

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the backend directory:

```env
DATABASE_URL="your_database_connection_string"
ANALYST_DATABASE_URL="your_read_only_database_connection_string"
OPENROUTER_API_KEY="your_openrouter_api_key"
```
(An example env file has been provided)  
The analyst connection should use a restricted, read-only database role.

Then run:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at: `http://127.0.0.1:8000`  
To access api docs, navigate to: `http://127.0.0.1:8000/docs`


### Configure the frontend

In the frontend directory:

```bash
cd frontend
pnpm install
```
Create a `.env.local` file in the frontend directory:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

This variable configures the frontend to communicate with the local FastAPI backend.

Start the frontend using:
```bash
pnpm run dev
```
Then go to `http://localhost:5173` to access the frontend



## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Checks backend and database connectivity |
| `GET` | `/schema` | Returns database schema metadata |
| `POST` | `/analyze` | Generates SQL, validates and executes it, and returns analysis results |




## Testing

Run the backend test suite from the backend directory:

```bash
pytest -v
```
---

Future Fix:
- Add a backup model so that it auto switches to second model if the first model is down.
