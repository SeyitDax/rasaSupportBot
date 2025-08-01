### API Endpoints

#### Create a Reminder

- **POST** `/api/reminders`
- **Body:**
  ```json
  {
    "to": "+1234567890",
    "message": "Your reminder message",
    "created_at": "2025-07-01T15:00:00"
  }
  ```
- **Response:**
  ```json
  { "message": "Reminder scheduled", "reminder_id": 1 }
  ```

#### List All Reminders

- **GET** `/api/reminders`
- **Response:** List of reminders

#### Get a Specific Reminder

- **GET** `/api/reminders/<reminder_id>`

#### Delete a Reminder

- **DELETE** `/api/reminders/<reminder_id>`

#### Delete All Past Reminders

- **DELETE** `/api/reminders/past`
- **Response:** `{ "message": "X past reminders deleted." }`

#### Health Check

- **GET** `/health`
- **Response:** `{ "status": "ok" }`

---