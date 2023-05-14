# DocExtractor-NFI

## API Endpoints


### 1. Upload PDF and Start Entity Extraction

**Endpoint:** `POST /api/extract_entities`

**Description:** Upload a PDF file and start the entity extraction process.

**Parameters:**

- `prompt_template` (optional, string): A custom extraction template. Keep it empty
- `pdf` (required, file): The PDF file to be processed.

**Response:** A unique `key` associated with the submitted task.

```json
{
  "key": "example-unique-key"
}


```
**Example:** 

```json
curl -X POST -F "pdf=@1076.25 COA.pdf" http://13.127.170.248:8000/api/extract_entities

This returns a key, Example:

{"key":"b7827c1c-b6a4-4ca2-906e-77c1344c46d0"}
```




### 2. Check Task Status

**Endpoint:** GET /api/check_status/{key}

**Description:** Check the status of a submitted task using the provided key.

**Parameters:**

- `key` (required, string): The unique key associated with the submitted task.

**Response:** A unique `key` associated with the submitted task.

```json
{
  "status": "completed",
  "result_url": "https://example-bucket.s3.amazonaws.com/example-unique-key.json"
}

```

**Example:** 

```json

curl -X GET http://13.127.170.248:8000/api/check_status/b7827c1c-b6a4-4ca2-906e-77c1344c46d0

This returns a key, Example:

{"status": "processing"}

when done, response will be:

{
  "status": "completed",
  "result_url": "https://example-bucket.s3.amazonaws.com/b7827c1c-b6a4-4ca2-906e-77c1344c46d0.json"
}


```


### 3. Get Extracted Entities

**Endpoint:** GET /api/get_results/{key}

**Description:** Retrieve the extracted entities for a completed task using the provided key.

**Parameters:**

- `key` (required, string): The unique key associated with the submitted task.

**Response:** Extracted entities in JSON format.


**Example:** 

```json

curl -X GET http://13.127.170.248:8000/api/get_results/b7827c1c-b6a4-4ca2-906e-77c1344c46d0

{
    "Supplier Information": {
        "Vendor Name": "Nutrisol",
        "Supplier Name": "N/A",
        "Supplier Code": "N/A",
        "Raw Material Supplier": "N/A",
        "RM Supplier Code": "N/A",
        "Key RM Identifiers": "N/A"
    },
    "Product/Raw Material Information": {
        "Name": "L-Selenomethionine Trit 0.5% Se",
        "Product Code": "SE25050106",
        "Ingredient Type": "N/A",
        "Potency": "N/A",
        "Category": "N/A",
        "CAS Number": "N/A",
        "Botanical Name": "N/A",
        "Active Ingredient": "N/A",
        "Active Ingredient %": "0.50 0.75%",
        "Unit of Measure": "ICP",
        "Form": "0.57%"
    },
} 
```