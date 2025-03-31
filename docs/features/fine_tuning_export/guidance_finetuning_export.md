# Guidance: Using Chat History for LLM Fine-Tuning

This document provides guidance on how to implement a feature to extract chat history data from the `oui-backend` database for the purpose of fine-tuning Large Language Models (LLMs).

**Disclaimer:** This feature is not natively implemented. Implementing it requires careful consideration of technical aspects, data privacy, and user consent.

## Proposed Architecture & Components

A dedicated module or set of scripts would be needed to handle the extraction, processing, and formatting. This could potentially be exposed via an admin-only API endpoint or run as a separate utility script.

**Key Components:**

1.  **`FineTuningExporter` (New Component/Script):**
    *   Responsible for orchestrating the export process.
    *   Takes parameters like date ranges, user IDs (or flags for anonymization/consent), target format, filtering criteria.
    *   Interacts with Data Access Layers (`ChatTable`, `MessageTable`, `UserTable`) to fetch data.
    *   Calls `DataProcessor` to clean and format the data.
    *   Outputs the final dataset file(s).

2.  **`DataProcessor` (New Component/Utility):**
    *   Handles cleaning, anonymization (PII scrubbing), and formatting of raw message data.
    *   Transforms conversation turns into the required fine-tuning format (e.g., prompt/completion pairs, JSONL).
    *   May need configurable rules for filtering low-quality interactions or system messages.

3.  **`Admin API Endpoint` (Optional - New in `routers/admin.py` or similar):**
    *   An endpoint (e.g., `/api/v1/admin/fine-tuning/export`) secured for admin users (`Depends(get_admin_user)`).
    *   Accepts export parameters (filters, format).
    *   Triggers the `FineTuningExporter` (potentially as a background task for large exports).
    *   Returns the status or allows downloading the resulting dataset file.

4.  **Consent/Metadata Handling (Enhancement):**
    *   Consider adding fields to the `User` or `Chat` models/tables to track user consent for fine-tuning data usage.
    *   The `FineTuningExporter` **must** respect these consent flags.

## Workflow (Example: Admin-Triggered Export)

1.  **Admin Request:** Admin user accesses the UI/API endpoint to initiate an export, specifying parameters (date range, format, consent requirements met).
2.  **API Handling:** The `Admin API Endpoint` receives the request, validates parameters, and authenticates the admin user.
3.  **Export Trigger:** The endpoint calls the `FineTuningExporter`.
4.  **Data Fetching:** `FineTuningExporter` queries `MessageTable` and potentially `ChatTable`/`UserTable`, filtering based on provided parameters AND consent flags.
5.  **Data Processing:** Fetched raw messages/chats are passed to the `DataProcessor`.
6.  **Cleaning & Formatting:** `DataProcessor` scrubs PII (if configured), filters unwanted messages, and formats the conversations into the target structure (e.g., JSONL).
7.  **Output Generation:** `FineTuningExporter` saves the formatted data to a file.
8.  **Response/Notification:** The API endpoint returns a success message, possibly with a link to download the file or indicating that the background task is running.

## Data Extraction Logic (Core Query)

The core logic within `FineTuningExporter` would involve querying the `message` table, potentially joining with `chat` and `user`:

```sql
-- Pseudocode SQL - Adapt for SQLAlchemy
SELECT
    m.id AS message_id,
    m.channel_id AS chat_id,
    m.user_id,        -- For filtering/consent checks
    u.role AS user_role, -- To differentiate user/assistant (might be stored differently)
    m.content,
    m.created_at,
    c.meta AS chat_metadata -- e.g., model used
FROM
    message m
JOIN
    chat c ON m.channel_id = c.id
JOIN
    "user" u ON m.user_id = u.id -- Or determine role differently
WHERE
    c.user_id IN (<list_of_consenting_user_ids>) -- CRITICAL CONSENT FILTER
    AND m.created_at BETWEEN <start_date> AND <end_date>
    -- Add other filters (e.g., chat quality flags if implemented)
ORDER BY
    m.channel_id, m.created_at;
```

*(Note: Determining the "role" (user vs. assistant) might require inspecting the `Message.meta` field, the `Message.user_id` compared to the `Chat.user_id`, or the sequence of messages within the `Chat.chat` JSON blob, depending on how assistant messages are stored).*

## Privacy Considerations (CRITICAL)

*   **Consent:** Never use user data without explicit, informed consent specifically for fine-tuning purposes. Implement robust consent tracking.
*   **Anonymization/PII Scrubbing:** Implement reliable techniques to remove names, emails, addresses, and other PII before using the data. This is non-trivial. Consider using NLP libraries or specialized services.
*   **Data Minimization:** Only extract the data absolutely necessary for fine-tuning.
*   **Security:** Secure the export process and the resulting dataset files appropriately.
*   **Compliance:** Ensure compliance with GDPR, CCPA, and other relevant regulations.

## Implementation Steps

1.  **Design Consent Mechanism:** Decide how and where user consent will be stored and managed.
2.  **Develop `DataProcessor`:** Implement cleaning, PII scrubbing (this is the hardest part), and formatting logic.
3.  **Develop `FineTuningExporter`:** Implement data fetching logic (using SQLAlchemy, respecting consent) and integrate with `DataProcessor`.
4.  **(Optional) Develop Admin API Endpoint:** Create the FastAPI endpoint, handle request parameters, trigger the exporter, and manage responses/file downloads.
5.  **Testing:** Thoroughly test the entire pipeline, especially the PII scrubbing and consent filtering. 