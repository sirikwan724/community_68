# Class Diagram - ระบบจัดการชุมชน

```mermaid
classDiagram

%% ─────────────────────────────────────────
%% ACCOUNTS APP
%% ─────────────────────────────────────────

class AbstractUser {
    <<Django Built-in>>
    +id: int
    +username: str
    +password: str
    +email: str
    +is_active: bool
    +is_staff: bool
}

class User {
    +full_name: str
    +address: str
    +citizen_id: str
    +house_owner_name: str
    +phone: str
    +prefix: str
    +birth_date: date
    +role: str
    +verified: bool
}

class Profile {
    +id: int
    +full_name: str
    +phone_number: str
}

class RegistrationRequest {
    +id: int
    +username: str
    +full_name: str
    +phone: str
    +address: str
    +citizen_id: str
    +house_owner_name: str
    +prefix: str
    +birth_date: date
    +password: str
    +status: str
    +created_at: datetime
}

class News {
    +id: int
    +title: str
    +content: str
    +image: image
    +created_at: datetime
    +updated_at: datetime
}

class HeadmanStatus {
    +id: int
    +is_online: bool
    +updated_at: datetime
}

%% ─────────────────────────────────────────
%% VILLAGE APP
%% ─────────────────────────────────────────

class Village {
    +id: int
    +name: str
    +description: str
    +address: str
    +latitude: decimal
    +longitude: decimal
    +updated_at: datetime
}

class VillageSection {
    +id: int
    +type: str
    +title: str
    +content: str
    +description: str
    +order: int
    +created_at: datetime
    +updated_at: datetime
}

class VillageSectionImage {
    +id: int
    +image: image
    +caption: str
    +order: int
    +created_at: datetime
}

class VillagePlace {
    +id: int
    +name: str
    +detail: str
    +order: int
}

class VillagePlaceImage {
    +id: int
    +image: image
    +caption: str
    +order: int
    +created_at: datetime
}

class CommunityProfile {
    +id: int
    +group: str
    +prefix: str
    +position: str
    +level: int
    +full_name: str
    +phone: str
    +email: str
    +description: str
    +image: image
    +is_active: bool
}

class FundType {
    +id: int
    +name: str
    +description: str
    +is_active: bool
}

class FundRecord {
    +id: int
    +year: int
    +interest_rate: decimal
    +last_uploaded_file: str
    +created_at: datetime
    +updated_at: datetime
}

class FundLoan {
    +id: int
    +full_name: str
    +bank_account: str
    +loan_amount: decimal
    +interest_amount: decimal
    +purpose: str
    +created_at: datetime
}

%% ─────────────────────────────────────────
%% REPORTS APP
%% ─────────────────────────────────────────

class Report {
    +id: int
    +fullname: str
    +phone: str
    +category: str
    +description: str
    +area: str
    +image: image
    +status: str
    +created_at: datetime
}

class ReportNote {
    +id: int
    +text: str
    +created_at: datetime
}

class RequestHelp {
    +id: int
    +request_type: str
    +start_datetime: datetime
    +end_datetime: datetime
    +detail: str
    +area: str
    +file: file
    +reject_reason: str
    +status: str
    +created_at: datetime
    +updated_at: datetime
}

class Appointment {
    +id: int
    +meet_with: str
    +meeting_place: str
    +date: date
    +start_time: time
    +end_time: time
    +reason: str
    +status: str
    +admin_note: str
    +created_at: datetime
}

%% ─────────────────────────────────────────
%% BORROW APP
%% ─────────────────────────────────────────

class Location {
    +id: int
    +name: str
    +is_active: bool
}

class Item {
    +id: int
    +name: str
    +unit: str
    +stock: int
    +is_active: bool
}

class BorrowRequest {
    +id: int
    +borrower_name: str
    +borrower_phone: str
    +borrow_type: str
    +start_datetime: datetime
    +end_datetime: datetime
    +pickup_datetime: datetime
    +expected_return_datetime: datetime
    +purpose: str
    +image: image
    +status: str
    +admin_note: str
    +created_at: datetime
}

class BorrowItem {
    +id: int
    +quantity: int
}

%% ─────────────────────────────────────────
%% PUBLIC SERVICE APP
%% ─────────────────────────────────────────

class PublicService {
    +id: int
    +name: str
    +category: str
    +location: str
    +description: str
    +status: str
    +image: image
    +created_at: datetime
}

class PublicServiceReport {
    +id: int
    +title: str
    +description: str
    +image: image
    +status: str
    +created_at: datetime
}

%% ─────────────────────────────────────────
%% RELATIONSHIPS
%% ─────────────────────────────────────────

%% Inheritance
AbstractUser <|-- User

%% accounts
User "1" --> "0..1" Profile : has
User "1" --> "0..*" News : authors
User "1" --> "0..*" Report : submits
User "1" --> "0..*" RequestHelp : requests
User "1" --> "0..*" Appointment : makes
User "1" --> "0..*" Appointment : receives (meeting_person)
User "1" --> "0..*" BorrowRequest : borrows
User "1" --> "0..*" PublicServiceReport : reports

%% village
Village "1" --> "0..*" CommunityProfile : has
Village "1" --> "0..*" FundType : has
FundType "1" --> "0..*" FundRecord : has
FundRecord "1" --> "0..*" FundLoan : has
VillageSection "1" --> "0..*" VillageSectionImage : has
VillageSection "1" --> "0..*" VillagePlace : contains
VillagePlace "1" --> "0..*" VillagePlaceImage : has

%% reports
Report "1" --> "0..*" ReportNote : has

%% borrow
BorrowRequest "1" --> "0..*" BorrowItem : contains
BorrowItem "0..*" --> "1" Item : references
BorrowRequest "0..*" --> "0..1" Location : at

%% publicservice
PublicService "1" --> "0..*" PublicServiceReport : receives
```

---

## คำอธิบาย Enum Values

| คลาส | Field | ค่าที่เป็นไปได้ |
|------|-------|----------------|
| `User` | role | guest / user / admin / superadmin |
| `RegistrationRequest` | status | pending / approved / rejected |
| `VillageSection` | type | RICH / PLACES |
| `CommunityProfile` | group | leader / committee / volunteer |
| `Report` | status | pending / processing / resolved / canceled |
| `Report` | category | ไฟฟ้า / น้ำ / ถนน / บุคคล / เสียง / กลิ่น |
| `RequestHelp` | status | pending / approved / rejected / done / canceled |
| `RequestHelp` | request_type | เสียง / ปิดทาง / ทั้งสองอย่าง / อื่นๆ |
| `Appointment` | meet_with | headman / assistant_headman |
| `Appointment` | meeting_place | village_hall / temple / headman_office / learning_center |
| `Appointment` | status | pending / approved / canceled / rejected / done |
| `BorrowRequest` | borrow_type | ITEM / LOCATION |
| `BorrowRequest` | status | pending / approved / borrowed / return_requested / returned / rejected / cancelled |
| `PublicService` | category | water / washer / other |
| `PublicService` | status | normal / maintenance / broken |
| `PublicServiceReport` | status | pending / processing / resolved / canceled |
