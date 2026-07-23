# Trip Planner Assessment App

## Overview
A full-stack trip planning application built with Django and React. It accepts trip inputs, calculates route guidance, rest recommendations, remaining cycle hours, and generates ELD-style daily logs for dispatch planning.

## Problem
The goal was to create a practical planning tool that helps users evaluate a trip before departure. The solution needed to:
- accept trip inputs clearly
- calculate trip duration and duty-time impact
- flag rest and cycle-hour concerns
- return a structured plan suitable for operations and compliance-style reporting

## Approach
I used a backend-first implementation to keep the business logic reliable and testable.

### Backend
- Built with Django and Django REST Framework
- Implemented a dedicated trip-planning service that handles:
  - distance estimation
  - drive and on-duty hour calculation
  - cycle hour tracking
  - rest-break suggestions
  - multi-day trip handling
  - ELD-style daily log generation
  - route summary steps
- Added validation for required inputs and invalid values

### Frontend
- Built with React and Vite
- Connected to the Django API
- Designed a polished dashboard experience for entering trip details and viewing results

## Why This Approach
- Backend-first design keeps the core planning logic centralized and easier to test
- Clear separation between API, service logic, and UI improves maintainability
- The solution is easy to extend for future features such as map integration or richer operational rules

## Testing
The backend includes automated tests covering core functionality and validation.

### Test Cases Covered
- valid trip planning flow
- multi-day trip planning
- ELD log generation
- route summary generation
- missing required fields
- blank location values
- out-of-range cycle hours

### Edge Cases Covered
- trips that exceed daily drive/on-duty limits
- trips that approach or exceed cycle-hour limits
- invalid numeric input
- incomplete user submissions

## Run Locally
### Backend
```bash
source .venv/bin/activate
cd backend
python manage.py migrate
python manage.py runserver 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Notes
- Backend API health endpoint: `/api/health/`
- Trip planning endpoint: `/api/trip-plan/`
- Frontend runs locally at `http://127.0.0.1:5173`

## Result
The application delivers a usable, tested, and visually polished trip planning experience that is ready for assessment submission.
