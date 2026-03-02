# Public Grievance Tracker

A comprehensive full-stack web application that enables citizens to report grievances and track their progress in real-time. The platform provides a transparent and efficient system for grievance redressal with Aadhaar-based authentication and progress monitoring.

## Features

### For Citizens
- **Aadhaar-based Authentication**: Secure login using 12-digit Aadhaar number
- **Grievance Submission**: Submit grievances with photo evidence and detailed descriptions
- **Real-time Progress Tracking**: Monitor grievance progress with visual progress bars
- **Status Updates**: Receive live updates on grievance status and resolution
- **Mobile Responsive**: Optimized for all devices and screen sizes
- **Transparent Process**: Full visibility into grievance resolution timeline

### For Government Officials
- **Admin Dashboard**: Comprehensive management interface with analytics
- **Grievance Management**: View, update, and track grievances in assigned jurisdiction
- **Progress Tracking**: Update grievance progress with percentage-based tracking
- **Analytics & Reporting**: Visual charts and statistics for better decision making
- **Status Management**: Update grievance status (Submitted → In Progress → Resolved)

### Key Capabilities
- **Smart Location Detection**: Automatically determines Panchayat vs Municipal jurisdiction
- **Multi-role System**: Separate interfaces for citizens and administrators
- **File Upload Support**: Image attachments for complaint evidence
- **Search & Filter**: Advanced filtering by location, category, and status
- **Responsive Design**: Bootstrap-based modern UI with custom styling
- **Real-time Updates**: Live status tracking and notifications

## Technology Stack

### Backend
- **Python Flask**: Web framework for API development
- **SQLAlchemy**: Database ORM for data management
- **Flask-Login**: User authentication and session management
- **SQLite**: Lightweight database for development and production

### Frontend
- **HTML5**: Semantic markup structure
- **CSS3**: Custom styling with Bootstrap integration
- **JavaScript**: Interactive functionality and AJAX operations
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icon library for enhanced UX

### Database Schema
- **Users**: Citizen and admin account management
- **Locations**: State, district, village mapping with area type classification
- **Complaints**: Grievance tracking with status management
- **Announcements**: Digital governance content management

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EPICS
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - The application will automatically create the database and sample data

## Usage Guide

### For Citizens

1. **Registration**
   - Click "Register" and select "Citizen" as account type
   - Fill in username, email, and password
   - Accept terms and conditions

2. **Submit Complaint**
   - Login to your account
   - Click "Submit Complaint" from dashboard
   - Select your location (State → District → Village)
   - Choose complaint category and provide detailed description
   - Upload photo evidence (optional)
   - Submit the complaint

3. **Track Status**
   - View all your complaints in the dashboard
   - Check real-time status updates
   - Receive notifications when status changes

4. **View Announcements**
   - Browse latest announcements from your local authority
   - Filter by location, type, or search keywords
   - Get updates on meetings, schemes, and public notices

### For Government Officials

1. **Admin Access**
   - Use admin credentials: `admin` / `admin123`
   - Access admin dashboard with complaint management tools

2. **Manage Complaints**
   - View complaints assigned to your jurisdiction
   - Update complaint status (Pending → In Progress → Resolved)
   - Filter complaints by status or category

3. **Create Announcements**
   - Post public notices and meeting schedules
   - Share welfare scheme information
   - Update citizens on fund usage and development work

4. **Analytics**
   - View complaint statistics and resolution rates
   - Monitor performance metrics
   - Generate reports for higher authorities

## Sample Data

The application includes sample data for Hyderabad district:

### Urban Areas (Municipal)
- Amberpet
- Secunderabad
- Charminar
- Banjara Hills
- Jubilee Hills

### Rural Areas (Panchayat)
- Tirumalagiri
- Bandlaguda
- Maredpalle

### Demo Accounts
- **Citizen**: Aadhaar: `987654321098` (John Doe)
- **Admin**: Aadhaar: `123456789012` (Admin User)

## API Endpoints

### Authentication
- `POST /register` - User registration with Aadhaar
- `POST /login` - User login with Aadhaar
- `GET /logout` - User logout

### Grievances
- `GET /submit-complaint` - Grievance submission form
- `POST /submit-complaint` - Submit new grievance
- `POST /update-complaint-status/<id>` - Update grievance status and progress (admin)

### Announcements
- `GET /announcements` - View all announcements
- `GET /create-announcement` - Create announcement form (admin)
- `POST /create-announcement` - Publish new announcement (admin)

### API
- `GET /api/locations` - Get location data (JSON)

## File Structure

```
EPICS/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── citizen_dashboard.html
│   ├── admin_dashboard.html
│   ├── submit_complaint.html
│   ├── announcements.html
│   ├── create_announcement.html
│   ├── about.html
│   └── contact.html
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── main.js       # JavaScript functionality
│   └── uploads/          # File uploads directory
└── grievance_portal.db   # SQLite database (created automatically)
```

## Configuration

### Environment Variables
Create a `.env` file for production configuration:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///grievance_portal.db
UPLOAD_FOLDER=static/uploads
```

### Database Configuration
The application uses SQLite by default. For production, consider using PostgreSQL or MySQL by updating the `SQLALCHEMY_DATABASE_URI` in `app.py`.

## Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Login for secure user sessions
- **File Upload Security**: Secure filename handling and type validation
- **Input Validation**: Form validation and sanitization
- **Access Control**: Role-based access to different features

## Mobile Responsiveness

The application is fully responsive and optimized for:
- Desktop computers (1200px+)
- Tablets (768px - 1199px)
- Mobile phones (320px - 767px)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: support@telangana.gov.in,2410030520@klh.edu.in
- Phone: 1800-XXX-XXXX
- Documentation: [Portal Documentation](link-to-docs)

## Roadmap

### Phase 2 Features
- [ ] SMS/Email notifications
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Integration with government databases
- [ ] AI-powered complaint categorization
- [ ] Public feedback system
- [ ] Performance metrics tracking

### Phase 3 Features
- [ ] Blockchain-based transparency
- [ ] IoT integration for monitoring
- [ ] Advanced reporting tools
- [ ] Citizen satisfaction surveys
- [ ] Integration with other government portals
- [ ] Automated workflow management

## Acknowledgments

- Government of Telangana for the initiative
- Bootstrap team for the UI framework
- Flask community for the web framework
- All contributors and testers

---

**Built with ❤️ for the citizens of Telangana**
