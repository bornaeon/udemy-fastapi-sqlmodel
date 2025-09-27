# Video Management API

A modern FastAPI application for managing videos and categories using SQLModel, featuring both REST API endpoints and HTML forms for user interaction.<br />
From the Udemy course: <a href="https://www.udemy.com/course/hands-on-beginner-fastapi-and-sqlmodel/">Hands-On Beginner FastAPI and SQLModel</a>.

## 🚀 Features

- **RESTful API**: Complete CRUD operations for videos and categories
- **HTML Forms**: User-friendly web interface for video management
- **Database Integration**: SQLModel with SQLite database
- **Soft Delete**: Videos are soft-deleted (marked as inactive) instead of permanent deletion
- **Category Management**: Full category lifecycle with validation
- **Video-Category Relationships**: Join queries to display categorized videos
- **Modern Architecture**: Clean separation of concerns with routers and services

## 📁 Project Structure

```
├── main.py                  # Main FastAPI application
├── models.py                # SQLModel data models
├── database.py              # Database configuration
├── routers/                 # API route handlers
│   ├── __init__.py
│   ├── categories.py        # Category CRUD operations
│   ├── videos.py            # Video CRUD operations  
│   ├── forms.py             # HTML form handling
│   └── joins.py             # Complex queries with joins
├── services/                # Business logic and utilities
│   ├── __init__.py
│   └── validation.py        # Validation functions
├── templates/               # Jinja2 HTML templates
│   ├── layout.html
│   ├── form_add_video.html
│   ├── form_edit_video.html
│   └── form_list_video.html
├── static/                  # Static files (CSS, JS, images)
│   └── styles.css
└── database.db              # SQLite database file
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- Conda (recommended) or pip

### Using Conda (Recommended)

1. **Create a new conda environment:**
   ```bash
   conda create -n video-api python=3.11
   conda activate video-api
   ```

2. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn sqlmodel jinja2 python-multipart
   ```

3. **Run the application:**
   ```bash
   uvicorn main:api --reload
   ```

### Using pip

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn sqlmodel jinja2 python-multipart
   ```

3. **Run the application:**
   ```bash
   uvicorn main:api --reload
   ```

## 🚀 Running the Application

### Development Mode (with auto-reload)

```bash
uvicorn main:api --reload
```

### Production Mode

```bash
uvicorn main:api --host 0.0.0.0 --port 8000
```

The application will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Home Page**: http://localhost:8000/

## 📚 API Endpoints

### Categories
- `GET /api/category` - Get all categories
- `GET /api/category/{category_id}` - Get a specific category
- `POST /api/category` - Create a new category
- `PUT /api/category/{category_id}` - Update a category
- `DELETE /api/category/{category_id}` - Delete a category

### Videos
- `GET /api/video` - Get all active videos
- `GET /api/video/{video_id}` - Get a specific video
- `POST /api/video` - Create a new video
- `PUT /api/video/{video_id}` - Update a video
- `DELETE /api/video/{video_id}` - Soft delete a video
- `DELETE /api/video/{video_id}/undelete` - Restore a soft-deleted video

### Forms (HTML Interface)
- `GET /add_video_form` - Display add video form
- `POST /submit_video` - Submit new video data
- `GET /edit_video_form/{video_id}` - Display edit video form
- `POST /edit_video_form/{video_id}` - Submit edited video data
- `GET /delete_video_form/{video_id}` - Delete a video
- `GET /list_video_form` - Display list of videos

### Joins & Complex Queries
- `GET /api/categorised_videos` - Get videos with category information
- `GET /list_video_form` - HTML page with categorized video list

## 🗄️ Database Models

### Category Model
```python
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
```

### Video Model
```python
class Video(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    youtube_code: str
    category_id: int = Field(foreign_key="category.id")
    is_active: bool = Field(default=True)
    date_created: datetime = Field(default_factory=datetime.now)
    date_last_modified: Optional[datetime] = None
```

## 🔧 Configuration

### Database
The application uses SQLite by default. The database file (`database.db`) will be created automatically when you first run the application.

### Static Files
Static files (CSS, JS, images) are served from the `/static` directory.

### Templates
HTML templates use Jinja2 and are located in the `/templates` directory.

## 🧪 Testing the API

### Using the Interactive Documentation
1. Visit http://localhost:8000/docs
2. Use the interactive interface to test endpoints
3. Click "Try it out" on any endpoint to test it

### Using curl Examples

**Create a category:**
```bash
curl -X POST "http://localhost:8000/api/category" \
     -H "Content-Type: application/json" \
     -d '{"name": "Tutorials"}'
```

**Create a video:**
```bash
curl -X POST "http://localhost:8000/api/video" \
     -H "Content-Type: application/json" \
     -d '{"title": "FastAPI Tutorial", "youtube_code": "abc123", "category_id": 1}'
```

**Get all videos:**
```bash
curl -X GET "http://localhost:8000/api/video"
```

## 🏗️ Architecture

### FastAPI Best Practices Applied

1. **Router Organization**: Each domain (categories, videos, forms, joins) has its own router
2. **Service Layer**: Business logic separated from route handlers
3. **Proper Session Management**: Database sessions managed with context managers
4. **Error Handling**: Consistent HTTP status codes and error messages
5. **Type Hints**: Full type annotation support
6. **Documentation**: Automatic OpenAPI documentation generation

### Key Components

- **Routers**: Handle HTTP requests and responses
- **Services**: Contain business logic and validation
- **Models**: Define data structures and database schema
- **Templates**: Render HTML responses
- **Static Files**: Serve CSS and other assets

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**: Change the port with `--port 8001`
2. **Database errors**: Delete `database.db` to reset the database
3. **Import errors**: Ensure all dependencies are installed
4. **Template not found**: Check that templates are in the correct directory

### Debug Mode

Run with debug information:
```bash
uvicorn main:api --reload --log-level debug
```

## 📝 Development Notes

- The application uses soft deletes for videos (setting `is_active = False`)
- Categories cannot be deleted if they have associated videos
- All database operations use proper session management
- The application follows RESTful conventions
- HTML forms provide a user-friendly interface alongside the API

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.
