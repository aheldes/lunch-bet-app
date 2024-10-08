# lunch-bet-app

## Requirements

- Python 3.12
- Node.js (for the frontend)

## Getting Started

Follow these instructions to set up and run the project locally.

### Backend Setup

1.  **Create a Virtual Environment:**

```bash
python  -m  venv  venv
```

2.  **Activate the Virtual Environment:**

- On Windows:

```bash
venv\Scripts\activate
```

- On macOS/Linux

```bash
source  venv/bin/activate
```

3.  **Install Dependencies**

```bash
pip  install  -r  requirements.txt
```

4.  **Run**

- Firsly run redis and pg containers

```bash
docker-compose up
```

- Using make

```bash
make  run-locally
```

- Using uvicorn directly

```bash
cd be
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### FE setup

1.  **Navigate to Frontend directory**

```bash
cd  fe
```

2. Install dependencies

```bash
npm  install
```

3. Run frontend

```basah
npm run dev
```
