import zlib, base64, urllib.request, os

def plantuml_encode(text):
    """Encode PlantUML text for URL"""
    data = text.encode('utf-8')
    compressed = zlib.compress(data)[2:-4]  # strip zlib header/checksum
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    result = ""
    for i in range(0, len(compressed), 3):
        chunk = compressed[i:i+3]
        b = [c for c in chunk] + [0] * (3 - len(chunk))
        result += alphabet[(b[0] >> 2) & 0x3F]
        result += alphabet[((b[0] & 0x3) << 4) | ((b[1] >> 4) & 0xF)]
        result += alphabet[((b[1] & 0xF) << 2) | ((b[2] >> 6) & 0x3)]
        result += alphabet[b[2] & 0x3F]
    return result[:len(result) - (3 - len(compressed) % 3) % 3] if len(compressed) % 3 else result

def save_diagram(puml_text, filename):
    encoded = plantuml_encode(puml_text)
    url = f"https://www.plantuml.com/plantuml/png/{encoded}"
    print(f"Downloading {filename}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        with open(filename, 'wb') as f:
            f.write(response.read())
    print(f"  Saved: {filename}")

# ─────────────────────────────────────────────────────────────────
# Flow 1 — User Login
# ─────────────────────────────────────────────────────────────────
flow1 = """
@startuml
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true
skinparam ParticipantPadding 30
skinparam BoxPadding 10
skinparam defaultFontName TH Sarabun New
skinparam defaultFontSize 13

title Flow 1 — User Login

actor "ผู้ใช้งาน\\n(User)" as User
participant "Frontend\\n(Vue)" as FE
participant "Backend API\\n(Django)" as API
participant "Database" as DB

User -> FE : กรอก username + password
activate FE

FE -> API : POST /api/accounts/login/\\n{username, password}
activate API

API -> DB : SELECT user WHERE username=?
activate DB
DB --> API : user record
deactivate DB

alt [credentials ถูกต้อง]
    API -> API : ตรวจสอบ password hash
    API -> API : สร้าง JWT token\\n(แนบ role, full_name)
    API --> FE : 200 OK\\n{access, refresh, role, user{...}}
    FE -> FE : บันทึก token ใน localStorage
    FE --> User : เปลี่ยนหน้าไป Dashboard
else [credentials ผิด]
    API --> FE : 401 Unauthorized
    FE --> User : แสดง error\\n"ข้อมูลไม่ถูกต้อง"
end

deactivate API
deactivate FE

@enduml
"""

# ─────────────────────────────────────────────────────────────────
# Flow 2 — Register Request + Admin Approve/Reject
# ─────────────────────────────────────────────────────────────────
flow2 = """
@startuml
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true
skinparam ParticipantPadding 20
skinparam BoxPadding 10
skinparam defaultFontName TH Sarabun New
skinparam defaultFontSize 12

title Flow 2 — Register Request + Admin Approve/Reject

actor "ผู้ใช้งาน\\n(User)" as User
actor "Admin" as Admin
participant "Frontend\\n(Vue)" as FE
participant "Backend API\\n(Django)" as API
participant "Database" as DB

== ขั้นตอนสมัคร ==

User -> FE : กรอกฟอร์มสมัคร
activate FE

FE -> API : POST /api/accounts/register-request/\\n{username, full_name, phone, address,\\ncitizen_id, house_owner_name, password}
activate API

API -> DB : ตรวจ username ซ้ำ?
activate DB
DB --> API : result
deactivate DB

alt [username ซ้ำ]
    API --> FE : 400 Bad Request\\n{username: ["ชื่อผู้ใช้งานนี้ถูกใช้แล้ว"]}
    FE --> User : แสดง error
else [อายุ < 18 ปี]
    API --> FE : 400 Bad Request\\n{birth_date: ["ผู้สมัครต้องมีอายุ 18 ปีขึ้นไป"]}
    FE --> User : แสดง error
else [ข้อมูลถูกต้อง]
    API -> API : hash password
    API -> DB : INSERT RegistrationRequest\\n(status = "pending")
    activate DB
    DB --> API : saved
    deactivate DB
    API --> FE : 201 Created\\n{"message": "ส่งคำขอสมัครสำเร็จ รอผู้ใหญ่บ้านอนุมัติ"}
    FE --> User : แสดงข้อความรอการอนุมัติ
end

deactivate API
deactivate FE

== ขั้นตอน Admin ==

Admin -> FE : เข้าหน้า /admin/users/approve
activate FE
FE -> API : GET /api/accounts/admin/requests/
activate API
API -> DB : SELECT RegistrationRequest\\nWHERE status = "pending"
activate DB
DB --> API : list of requests
deactivate DB
API --> FE : รายการคำขอทั้งหมด
FE --> Admin : แสดงรายการรอการอนุมัติ

alt [Admin อนุมัติ]
    Admin -> FE : กดปุ่ม "อนุมัติ"
    FE -> API : POST /admin/requests/{id}/approve/
    API -> DB : BEGIN TRANSACTION\\nINSERT User (role="user", verified=true)\\nUPDATE RegistrationRequest status="approved"\\nCOMMIT
    activate DB
    DB --> API : success
    deactivate DB
    API --> FE : 200 OK\\n{"message": "อนุมัติสำเร็จ", "user_id": ...}
    FE --> Admin : แสดงผลสำเร็จ
else [Admin ปฏิเสธ]
    Admin -> FE : กดปุ่ม "ปฏิเสธ"
    FE -> API : POST /admin/requests/{id}/reject/
    API -> DB : UPDATE RegistrationRequest\\nstatus = "rejected"
    activate DB
    DB --> API : success
    deactivate DB
    API --> FE : 200 OK\\n{"message": "ปฏิเสธสำเร็จ"}
    FE --> Admin : แสดงผลสำเร็จ
end

deactivate API
deactivate FE

@enduml
"""

os.makedirs("C:/commu/diagrams", exist_ok=True)
save_diagram(flow1, "C:/commu/diagrams/flow1_login.png")
save_diagram(flow2, "C:/commu/diagrams/flow2_register.png")
print("\nDone! All diagrams saved in C:/commu/diagrams/")
