# YouConv
Responsive Youtube Video Converter
- UI for mobile and desktop devices.
- Auto path finding and video search algorithm.

![preview](/static/images/preview1.png)

## Project Structure

The project is organized into separate backend and frontend directories:

```
YoutubeConverter/
├── backend/          # Django backend files
│   ├── manage.py     # Django management script
│   ├── cfe/          # Django project configuration
│   ├── youtube/      # Main application
│   ├── media/        # Downloaded files
│   └── db.sqlite3    # Database
├── frontend/         # Frontend assets
│   ├── templates/    # HTML templates
│   └── static/       # CSS, JS, images
└── README.md
```

## Running the Application

Navigate to the backend directory and run:
```bash
cd backend
python manage.py runserver
```

# Release v1.2
 - Now it allows users to request multiple downloads, query implemented.
 - Status page implemented users can see their download statuses.

# Release v1.3
 - Now Users can authenticate and see their queue
 - Navbar updated for authentication
 - Added feature to allow users to authenticate with email or username
 - Status page updated by removing the task id and adding the downloaded resources's title.
 - Status page automatically updated upon table change.
 - Download button redirects user to status page. 

 ![preview](/static/images/preview2.png)

# Upcoming Releases
- Status page style improvement.
- Better search and download algorithm.
- Friendship system that allows users to interact with each other and share their queries
