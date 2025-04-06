# Kern Resources Frontend

This directory contains the static website frontend for the Kern Resources project.

## Overview

The Kern Resources frontend is a simple static website that serves as the user interface for the Kern Resources application. It provides a clean, responsive design that allows users to search for and browse resources available in Kern County.

## Structure

```
frontend/
├── css/            # CSS stylesheets
├── public/         # Static assets (images, fonts, etc.)
├── src/            # JavaScript source files
├── index.html      # Main HTML file
└── README.md       # This file
```

## Features

- Responsive design that works on desktop and mobile devices
- Clean, modern user interface
- Search functionality (connects to backend API)
- Resource browsing and filtering
- Contact form

## Development

This is a simple static website that uses HTML, CSS, and vanilla JavaScript. No build tools or frameworks are required to develop or run the site.

### Local Development

To run the site locally, simply open the `index.html` file in a web browser.

### Deployment

The site is designed to be deployed on Render.com as a static site. Render will automatically build and deploy the site when changes are pushed to the repository.

#### Render Configuration

When setting up the site on Render:

1. Connect to the GitHub repository
2. Specify `frontend` as the root directory
3. No build command is needed for this simple static site
4. Publish directory should be `.` (the root of the frontend directory)

## Integration with Backend

In a production environment, this frontend will connect to the Kern Resources backend API to fetch resource data and perform searches. The API endpoints are configured in the JavaScript files.

## Browser Compatibility

The site is designed to work with modern browsers, including:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Future Enhancements

Planned enhancements for the frontend include:

1. Integration with the FTS5 search API
2. Advanced filtering options
3. User authentication
4. Resource saving and sharing
5. Mobile app-like experience with service workers
