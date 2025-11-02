# SafeTravel Server - DDD Architecture Guide

## 📚 Table of Contents
- [What is DDD?](#what-is-ddd)
- [Project Structure Overview](#project-structure-overview)
- [Layer Explanations](#layer-explanations)
- [Data Flow Example](#data-flow-example)
- [How to Add New Features](#how-to-add-new-features)
- [Common Patterns](#common-patterns)
- [FAQs](#faqs)

---

## 🎯 What is DDD?

**Domain-Driven Design (DDD)** is an approach to software development that focuses on the core business logic (the "domain") and keeps it separate from technical concerns like databases, APIs, or external services.

### Key Principles:
1. **Business logic is king** - Keep it pure and isolated
2. **Layers have clear responsibilities** - Each layer does ONE thing
3. **Dependencies flow inward** - Outer layers depend on inner layers, never the reverse
4. **Easy to test and maintain** - Change database? No problem. Change AI provider? Easy.

### The Layers (from inside out):
```
┌─────────────────────────────────────────┐
│   Domain Layer (Business Rules)         │  ← Core logic
├─────────────────────────────────────────┤
│   Application Layer (Use Cases)         │  ← Orchestration
├─────────────────────────────────────────┤
│   Infrastructure Layer (Tech Details)   │  ← Databases, APIs
├─────────────────────────────────────────┤
│   Presentation Layer (User Interface)   │  ← REST API, WebSocket
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure Overview

```
safetravel-server/
├── src/
│   ├── domain/              # 🧠 Business logic (pure Python, no frameworks)
│   ├── application/         # 🎯 Use cases (orchestrates domain logic)
│   ├── infrastructure/      # 🔧 Technical implementations (DB, APIs, AI)
│   ├── presentation/        # 🌐 User interfaces (REST, WebSocket)
│   ├── shared/             # 🛠️ Common utilities
│   └── config/             # ⚙️ Configuration
├── tests/                  # 🧪 All tests
├── logs/                   # 📝 Application logs
├── .env                    # 🔐 Secrets (DON'T COMMIT!)
└── requirements.txt        # 📦 Dependencies
```

---

## 🔍 Layer Explanations

### 1. Domain Layer (`src/domain/`)

**Purpose**: Contains pure business logic. No dependencies on databases, frameworks, or external services.

**What goes here**:
- **Entities**: Core business objects (User, Trip, Alert)
- **Value Objects**: Immutable values (Coordinate, SafetyScore)
- **Repository Interfaces**: Contracts for data access (no implementation!)
- **Domain Services**: Complex business logic that doesn't fit in entities
- **Events**: Things that happen in the domain (TripCreated, AlertTriggered)

**Example - Trip Entity**:
```python
# src/domain/entities/trip.py
class Trip:
    """
    A trip entity with business rules.
    Notice: No database code, no API code, just pure business logic!
    """
    
    def __init__(self, id, user_id, destination, start_date, end_date):
        self.id = id
        self.user_id = user_id
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.status = "planned"
    
    def start(self):
        """Business rule: Can only start a planned trip"""
        if self.status != "planned":
            raise ValueError("Can only start planned trips")
        self.status = "active"
    
    def complete(self):
        """Business rule: Can only complete active trips"""
        if self.status != "active":
            raise ValueError("Can only complete active trips")
        self.status = "completed"
```

**Example - Repository Interface** (Contract only, no implementation):
```python
# src/domain/repositories/trip_repository.py
from abc import ABC, abstractmethod

class ITripRepository(ABC):
    """
    Interface defining what a trip repository MUST do.
    Implementation details are in infrastructure layer!
    """
    
    @abstractmethod
    async def save(self, trip: Trip) -> Trip:
        pass
    
    @abstractmethod
    async def find_by_id(self, trip_id: str) -> Trip:
        pass
```

**Key Rule**: Domain layer has NO imports from other layers. It's completely independent.

---

### 2. Application Layer (`src/application/`)

**Purpose**: Orchestrates domain logic to fulfill use cases. This is where user actions get translated into domain operations.

**What goes here**:
- **Use Cases**: One use case per user action (CreateTrip, UpdateProfile, SendSOS)
- **DTOs**: Data Transfer Objects for communication between layers
- **Ports**: Interfaces for external services

**Example - Create Trip Use Case**:
```python
# src/application/use_cases/trip/create_trip.py
class CreateTripUseCase:
    """
    Orchestrates the creation of a new trip.
    Coordinates: validation, AI analysis, database saving, notifications
    """
    
    def __init__(
        self,
        trip_repository: ITripRepository,      # From domain
        safety_ai: SafetyPredictor,           # From infrastructure
        notification_service: INotificationService
    ):
        self.trip_repo = trip_repository
        self.safety_ai = safety_ai
        self.notifications = notification_service
    
    async def execute(self, user_id: str, destination: str, start_date, end_date):
        # 1. Calculate safety score using AI
        safety_data = await self.safety_ai.calculate_safety_score(
            destination=destination,
            waypoints=[],
            time_of_travel=start_date.isoformat()
        )
        
        # 2. Create trip entity (domain logic)
        trip = Trip.create(
            user_id=user_id,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            safety_score=safety_data["safety_score"]
        )
        
        # 3. Save to database
        saved_trip = await self.trip_repo.save(trip)
        
        # 4. Send notification
        await self.notifications.send(
            user_id=user_id,
            message=f"Trip to {destination} created successfully"
        )
        
        return saved_trip
```

**Key Rule**: Application layer imports from domain layer, but NOT from infrastructure or presentation.

---

### 3. Infrastructure Layer (`src/infrastructure/`)

**Purpose**: All the technical stuff - databases, external APIs, file systems, etc.

**What goes here**:
- **Database**: SQL, Firebase implementations
- **External Services**: Gemini AI, Google Maps, Weather API, Twilio
- **Auth**: JWT, Firebase Auth
- **Caching**: Redis
- **Messaging**: Event bus

**Structure**:
```
infrastructure/
├── database/
│   ├── sql/                    # PostgreSQL/MySQL
│   │   ├── models.py          # SQLAlchemy models
│   │   └── repositories/      # Repository implementations
│   └── firebase/              # Firebase Firestore
│       └── repositories/      # Firebase repository implementations
├── ai/
│   ├── gemini_client.py       # Base AI client
│   ├── safety_predictor.py    # Safety analysis
│   └── emergency_advisor.py   # Emergency help
├── external_services/
│   ├── google_maps_service.py
│   └── twilio_service.py
└── auth/
    └── jwt_service.py
```

**Example - Trip Repository Implementation**:
```python
# src/infrastructure/database/sql/repositories/trip_repository_impl.py
from src.domain.repositories.trip_repository import ITripRepository
from src.domain.entities.trip import Trip
from sqlalchemy.orm import Session

class TripRepositoryImpl(ITripRepository):
    """
    Concrete implementation of trip repository using PostgreSQL.
    Notice: Implements the interface from domain layer!
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def save(self, trip: Trip) -> Trip:
        # Convert domain entity to database model
        trip_model = TripModel(
            id=trip.id,
            user_id=trip.user_id,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            status=trip.status
        )
        
        self.db.add(trip_model)
        await self.db.commit()
        return trip
    
    async def find_by_id(self, trip_id: str) -> Trip:
        trip_model = await self.db.query(TripModel).filter(
            TripModel.id == trip_id
        ).first()
        
        # Convert database model back to domain entity
        return Trip(
            id=trip_model.id,
            user_id=trip_model.user_id,
            destination=trip_model.destination,
            start_date=trip_model.start_date,
            end_date=trip_model.end_date
        )
```

**Database Strategy**:
- **SQL (PostgreSQL)**: User profiles, trip history, safety reports (structured, permanent data)
- **Firebase Firestore**: Live GPS tracking, real-time alerts, active trip status (frequently changing data)

**Why both?**
- SQL is cheaper for large historical data
- Firebase excels at real-time updates with minimal latency
- Separation of concerns: permanent vs temporary data

---

### 4. Presentation Layer (`src/presentation/`)

**Purpose**: User-facing interfaces. How users interact with the system.

**What goes here**:
- **Controllers**: Handle HTTP requests
- **Routes**: Define API endpoints
- **Schemas**: Request/response validation (Pydantic)
- **Middlewares**: Auth, logging, error handling
- **WebSocket handlers**: Real-time communication

**Example - Trip Controller**:
```python
# src/presentation/http/controllers/trip_controller.py
from fastapi import APIRouter, Depends, HTTPException
from src.application.use_cases.trip.create_trip import CreateTripUseCase
from src.presentation.http.schemas.trip_schema import CreateTripRequest, TripResponse

router = APIRouter(prefix="/api/v1/trips", tags=["trips"])

@router.post("/", response_model=TripResponse, status_code=201)
async def create_trip(
    request: CreateTripRequest,
    use_case: CreateTripUseCase = Depends(get_create_trip_use_case)
):
    """
    API endpoint to create a new trip.
    Client sends JSON, we return JSON response.
    """
    try:
        trip = await use_case.execute(
            user_id=request.user_id,
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return TripResponse.from_entity(trip)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Key Rule**: Presentation layer only talks to application layer (use cases), never directly to domain or infrastructure.

---

## 🔄 Data Flow Example

Let's trace what happens when a user creates a trip:

```
📱 CLIENT (Mobile App)
    ↓
    POST /api/v1/trips
    { "destination": "Paris", "start_date": "2024-06-15", ... }
    ↓
┌─────────────────────────────────────────────────────┐
│ PRESENTATION LAYER                                  │
│ trip_controller.py receives request                 │
│ - Validates JSON schema (Pydantic)                  │
│ - Extracts user from JWT token                      │
└─────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────┐
│ APPLICATION LAYER                                   │
│ CreateTripUseCase.execute()                         │
│ - Orchestrates the workflow                         │
│ - Calls AI service to get safety score              │
│ - Creates Trip entity (domain)                      │
│ - Calls repository to save                          │
│ - Sends notifications                               │
└─────────────────────────────────────────────────────┘
    ↓                           ↓
┌─────────────────┐    ┌─────────────────────┐
│ DOMAIN LAYER    │    │ INFRASTRUCTURE      │
│ Trip.create()   │    │ - SafetyPredictor   │
│ Business rules  │    │   (Gemini AI)       │
│ - Validates     │    │ - TripRepository    │
│ - Enforces      │    │   (SQL database)    │
│   constraints   │    │ - Firebase          │
└─────────────────┘    │   (real-time)       │
                       └─────────────────────┘
    ↓
┌─────────────────────────────────────────────────────┐
│ Response travels back up                            │
│ TripResponse → Controller → JSON → Client           │
└─────────────────────────────────────────────────────┘
    ↓
📱 CLIENT receives created trip data
```

**Key Points**:
1. Client only sends HTTP request - no business logic on client
2. Each layer has clear responsibility
3. Domain layer stays pure - no database or API code
4. Infrastructure handles all technical details
5. Easy to test each layer independently

---

## 🆕 How to Add New Features

### Example: Adding "Share Trip with Friend" feature

#### Step 1: Domain Layer
Define what "sharing" means in business terms:

```python
# src/domain/entities/trip.py
class Trip:
    def share_with(self, friend_user_id: str):
        """Business rule: Can only share active or planned trips"""
        if self.status not in ["planned", "active"]:
            raise ValueError("Can only share planned or active trips")
        
        if friend_user_id in self.shared_with:
            raise ValueError("Trip already shared with this user")
        
        self.shared_with.append(friend_user_id)
```

#### Step 2: Application Layer
Create the use case:

```python
# src/application/use_cases/trip/share_trip.py
class ShareTripUseCase:
    def __init__(
        self,
        trip_repository: ITripRepository,
        notification_service: INotificationService
    ):
        self.trip_repo = trip_repository
        self.notifications = notification_service
    
    async def execute(self, trip_id: str, owner_user_id: str, friend_user_id: str):
        # 1. Get trip
        trip = await self.trip_repo.find_by_id(trip_id)
        
        # 2. Verify ownership
        if trip.user_id != owner_user_id:
            raise ValueError("Not authorized")
        
        # 3. Share (business logic in domain)
        trip.share_with(friend_user_id)
        
        # 4. Save
        await self.trip_repo.save(trip)
        
        # 5. Notify friend
        await self.notifications.send(
            user_id=friend_user_id,
            message=f"Trip to {trip.destination} shared with you"
        )
        
        return trip
```

#### Step 3: Presentation Layer
Add API endpoint:

```python
# src/presentation/http/routes/trip_routes.py
@router.post("/{trip_id}/share")
async def share_trip(
    trip_id: str,
    request: ShareTripRequest,
    current_user: dict = Depends(get_current_user),
    use_case: ShareTripUseCase = Depends()
):
    trip = await use_case.execute(
        trip_id=trip_id,
        owner_user_id=current_user["id"],
        friend_user_id=request.friend_user_id
    )
    return TripResponse.from_entity(trip)
```

#### Step 4: Test
```python
# tests/unit/application/test_share_trip.py
async def test_share_trip_success():
    # Arrange
    mock_repo = MockTripRepository()
    mock_notifications = MockNotificationService()
    use_case = ShareTripUseCase(mock_repo, mock_notifications)
    
    # Act
    result = await use_case.execute(
        trip_id="123",
        owner_user_id="user1",
        friend_user_id="user2"
    )
    
    # Assert
    assert "user2" in result.shared_with
    assert mock_notifications.sent_to == "user2"
```

---

## 🎨 Common Patterns

### 1. Dependency Injection

**What**: Pass dependencies through constructor instead of creating them inside.

**Why**: Makes testing easy, allows swapping implementations.

```python
# ❌ BAD - Hard to test
class CreateTripUseCase:
    def __init__(self):
        self.trip_repo = TripRepositoryImpl()  # Hardcoded!
        self.ai = SafetyPredictor()

# ✅ GOOD - Easy to test
class CreateTripUseCase:
    def __init__(
        self,
        trip_repository: ITripRepository,  # Interface, not implementation
        safety_ai: SafetyPredictor
    ):
        self.trip_repo = trip_repository
        self.ai = safety_ai

# In tests, pass mock implementations:
use_case = CreateTripUseCase(
    trip_repository=MockTripRepository(),  # Fake implementation
    safety_ai=MockSafetyPredictor()
)
```

### 2. Repository Pattern

**What**: Abstraction over data access. Domain defines WHAT it needs, infrastructure defines HOW.

**Why**: Easy to change database without touching business logic.

```python
# Domain defines interface
class ITripRepository(ABC):
    @abstractmethod
    async def save(self, trip: Trip) -> Trip:
        pass

# Infrastructure implements it
class PostgresTripRepository(ITripRepository):
    async def save(self, trip: Trip) -> Trip:
        # PostgreSQL implementation

class FirebaseTripRepository(ITripRepository):
    async def save(self, trip: Trip) -> Trip:
        # Firebase implementation

# Easy to swap!
```

### 3. Value Objects

**What**: Immutable objects representing values (not entities).

**Why**: Encapsulate validation, ensure consistency.

```python
# src/domain/value_objects/coordinate.py
class Coordinate:
    """Immutable coordinate with validation"""
    
    def __init__(self, latitude: float, longitude: float):
        if not -90 <= latitude <= 90:
            raise ValueError("Invalid latitude")
        if not -180 <= longitude <= 180:
            raise ValueError("Invalid longitude")
        
        self._latitude = latitude
        self._longitude = longitude
    
    @property
    def latitude(self) -> float:
        return self._latitude
    
    @property
    def longitude(self) -> float:
        return self._longitude
    
    # Can't be modified after creation!
```

---

## ❓ FAQs

### Q: Why is domain layer so isolated?

**A**: So business rules stay pure and don't get mixed with technical details. If we change from PostgreSQL to MongoDB, domain layer doesn't care!

### Q: Where do I put validation?

**A**: Depends!
- **Business validation** (Trip can't be longer than 365 days): Domain layer
- **Input validation** (Required fields, email format): Presentation layer (Pydantic schemas)

### Q: Can I import from infrastructure in application layer?

**A**: Yes! Application layer orchestrates, so it can use infrastructure implementations. But it should depend on interfaces, not concrete implementations.

```python
# ✅ GOOD
def __init__(self, trip_repository: ITripRepository):  # Interface

# ❌ BAD
def __init__(self, trip_repository: PostgresTripRepository):  # Concrete class
```

### Q: Where does Gemini AI code go?

**A**: Infrastructure layer (`src/infrastructure/ai/`). It's an external service.

### Q: Should I always use all layers?

**A**: For SafeTravel, yes. But for very simple apps, you might skip some layers. DDD is useful when business logic is complex.

### Q: How do I know what's a "domain concept"?

**A**: Ask: "Would business people understand this term?" 
- ✅ Trip, User, Safety Score, Emergency Contact → Domain concepts
- ❌ HTTP Request, Database Transaction, JSON → Technical details

### Q: What goes in shared/ folder?

**A**: Pure utilities that any layer can use: logger, date helpers, constants. No business logic!

---

## 🚀 Quick Start Checklist

When starting work on SafeTravel:

1. ✅ Read this guide
2. ✅ Set up `.env` with API keys
3. ✅ Run `pip install -r requirements.txt`
4. ✅ Understand the layer responsibilities
5. ✅ Look at existing code examples
6. ✅ Ask questions if unclear!

### Adding a new feature:
1. Start with domain: "What are the business rules?"
2. Create use case: "How does this feature work?"
3. Add infrastructure: "What external services do I need?"
4. Add API endpoint: "How does the client call this?"
5. Write tests: "Does it work?"

---

## 📖 Further Reading

- [Domain-Driven Design by Eric Evans](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)
- [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API Docs](https://ai.google.dev/docs)

---

## 💬 Questions?

If anything is unclear, ask the team! Understanding the architecture is crucial for writing maintainable code.

**Happy coding! 🎉**