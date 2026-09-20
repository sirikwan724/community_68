"""
OOP Demo - ระบบจัดการชุมชน
แสดงให้เห็น: PIE, Access Modifier, Overload & Override, Abstract Class, Interface
"""

from abc import ABC, abstractmethod
from typing import List


# ============================================================
# INTERFACE  (ABC ที่มีแต่ abstract method ล้วน = interface)
# ============================================================

class INotifiable(ABC):
    """Interface: ผู้ที่สามารถรับการแจ้งเตือนได้"""

    @abstractmethod
    def send_notification(self, message: str) -> str:
        pass


class IPayable(ABC):
    """Interface: ผู้ที่มีภาระค่าใช้จ่าย"""

    @abstractmethod
    def calculate_fee(self) -> float:
        pass

    @abstractmethod
    def pay(self, amount: float) -> str:
        pass


# ============================================================
# ABSTRACT CLASS
# ============================================================

class Person(ABC):
    """
    Abstract Class: คลาสแม่สำหรับบุคคลในระบบชุมชน
    ไม่สามารถสร้าง instance โดยตรงได้
    """

    # Class variable (public) — นับจำนวนประชากรทั้งหมด
    _population: int = 0

    def __init__(self, name: str, age: int, email: str):
        # Public attribute — เข้าถึงได้จากทุกที่
        self.name = name
        # Protected attribute — ควรใช้ภายใน class และ subclass เท่านั้น
        self._age = age
        # Private attribute — เข้าถึงได้เฉพาะภายใน class นี้
        self.__email = email

        Person._population += 1

    # ---- Encapsulation: Getter / Setter ผ่าน @property ----
    @property
    def email(self) -> str:
        """อ่านค่า email (private) ผ่าน property"""
        return self.__email

    @email.setter
    def email(self, value: str) -> None:
        if "@" in value:
            self.__email = value
        else:
            raise ValueError(f"รูปแบบ email ไม่ถูกต้อง: {value}")

    @property
    def age(self) -> int:
        return self._age

    @classmethod
    def get_population(cls) -> int:
        return cls._population

    # ---- Abstract Methods (บังคับให้ subclass ต้อง override) ----
    @abstractmethod
    def get_role(self) -> str:
        pass

    @abstractmethod
    def display_info(self) -> str:
        pass

    # ---- Concrete Method (subclass อาจ override หรือไม่ก็ได้) ----
    def introduce(self) -> str:
        return f"สวัสดี ฉันชื่อ {self.name} อายุ {self._age} ปี"

    def __str__(self) -> str:
        return f"{self.get_role()}: {self.name}"


# ============================================================
# CONCRETE CLASS 1 — Resident (สืบทอดจาก Person + 2 Interfaces)
# ============================================================

class Resident(Person, INotifiable, IPayable):
    """
    คลาสลูก: ผู้อยู่อาศัย
    Inheritance : Person
    Implements  : INotifiable, IPayable
    """

    def __init__(self, name: str, age: int, email: str,
                 house_number: str, village: str):
        super().__init__(name, age, email)
        self.house_number = house_number          # public
        self._village = village                   # protected
        self.__balance: float = 0.0               # private

    # ---- Override abstract methods ----
    def get_role(self) -> str:
        return "ผู้อยู่อาศัย"

    def display_info(self) -> str:
        return (f"[{self.get_role()}] ชื่อ: {self.name} | "
                f"บ้านเลขที่: {self.house_number} | หมู่บ้าน: {self._village}")

    # ---- Override concrete method (extend พฤติกรรมเดิม) ----
    def introduce(self) -> str:
        base = super().introduce()                # เรียก method ของ parent
        return f"{base} อาศัยอยู่บ้านเลขที่ {self.house_number}"

    # ---- Implement INotifiable ----
    def send_notification(self, message: str) -> str:
        return f"[SMS -> {self.name} ({self.house_number})]: {message}"

    # ---- Implement IPayable ----
    def calculate_fee(self) -> float:
        return 500.0  # ค่าส่วนกลางมาตรฐาน

    def pay(self, amount: float) -> str:
        if amount >= self.calculate_fee():
            self.__balance += amount
            return f"[OK] {self.name} ชำระค่าส่วนกลาง {amount:,.0f} บาท สำเร็จ"
        return (f"✗ เงินไม่พอ (ต้องการ {self.calculate_fee():,.0f} บาท "
                f"แต่จ่ายมา {amount:,.0f} บาท)")

    # ---- Method Overloading (Python ใช้ default parameters) ----
    def report_issue(self, title: str,
                     description: str = "",
                     priority: str = "ปกติ") -> str:
        """
        Overload 1: report_issue("น้ำไม่ไหล")
        Overload 2: report_issue("ไฟดับ", "บริเวณซอย 3", "ด่วน")
        """
        base = f"[{priority}] {title}"
        return f"แจ้งปัญหา: {base} — {description}" if description else f"แจ้งปัญหา: {base}"

    def get_balance(self) -> float:
        return self.__balance


# ============================================================
# CONCRETE CLASS 2 — Admin (สืบทอดจาก Person + INotifiable)
# ============================================================

class Admin(Person, INotifiable):
    """
    คลาสลูก: เจ้าหน้าที่ดูแลระบบ
    Inheritance : Person
    Implements  : INotifiable
    """

    def __init__(self, name: str, age: int, email: str,
                 employee_id: str, department: str):
        super().__init__(name, age, email)
        self.__employee_id = employee_id          # private
        self._department = department             # protected
        self.__permissions: List[str] = ["view", "edit"]

    def get_role(self) -> str:
        return "เจ้าหน้าที่"

    def display_info(self) -> str:
        return (f"[{self.get_role()}] ชื่อ: {self.name} | "
                f"แผนก: {self._department} | รหัส: {self.__employee_id}")

    def send_notification(self, message: str) -> str:
        return f"[ระบบ -> {self.name} / {self._department}]: {message}"

    def get_employee_id(self) -> str:
        return self.__employee_id

    def add_permission(self, permission: str) -> None:
        if permission not in self.__permissions:
            self.__permissions.append(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.__permissions

    # ---- Method Overloading ด้วย default parameters ----
    def approve_request(self, request_id: int,
                        note: str = "",
                        notify: bool = True) -> str:
        """
        Overload 1: approve_request(101)
        Overload 2: approve_request(102, "ผ่านการตรวจสอบ", False)
        """
        result = f"✓ อนุมัติคำร้อง #{request_id}"
        if note:
            result += f" | หมายเหตุ: {note}"
        if notify:
            result += " | (ส่งแจ้งเตือนแล้ว)"
        return result


# ============================================================
# CONCRETE CLASS 3 — VillageHead (Multi-level Inheritance)
# ============================================================

class VillageHead(Admin, IPayable):
    """
    คลาสลูก: ผู้ใหญ่บ้าน
    Inheritance : Admin -> Person  (Multi-level)
    Implements  : IPayable
    """

    def __init__(self, name: str, age: int, email: str,
                 employee_id: str, village_name: str):
        super().__init__(name, age, email, employee_id, "ผู้นำชุมชน")
        self.__village_name = village_name        # private
        self.__budget: float = 100_000.0          # private

    # ---- Override (อีกครั้ง จาก Admin -> Person) ----
    def get_role(self) -> str:
        return "ผู้ใหญ่บ้าน"

    def display_info(self) -> str:
        return (f"[{self.get_role()}] ชื่อ: {self.name} | "
                f"หมู่บ้าน: {self.__village_name} | "
                f"งบประมาณคงเหลือ: {self.__budget:,.2f} บาท")

    def introduce(self) -> str:
        return (f"สวัสดีครับ ผม{self.name} ผู้ใหญ่บ้าน{self.__village_name} "
                f"ยินดีต้อนรับทุกท่าน")

    # ---- Implement IPayable ----
    def calculate_fee(self) -> float:
        return 0.0  # ผู้ใหญ่บ้านได้รับการยกเว้น

    def pay(self, amount: float) -> str:
        return f"ℹ {self.name} ได้รับการยกเว้นค่าส่วนกลาง"

    def allocate_budget(self, project: str, amount: float) -> str:
        if amount <= self.__budget:
            self.__budget -= amount
            return (f"✓ จัดสรร {amount:,.0f} บาท → '{project}' | "
                    f"คงเหลือ: {self.__budget:,.2f} บาท")
        return (f"✗ งบไม่พอ (มี {self.__budget:,.2f} บาท "
                f"แต่ต้องการ {amount:,.0f} บาท)")


# ============================================================
# DEMONSTRATION FUNCTIONS
# ============================================================

def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def demo_polymorphism(persons: List[Person]) -> None:
    section("POLYMORPHISM — เรียก display_info() / introduce() บน type ต่างกัน")
    for p in persons:
        print(f"  {p.display_info()}")
        print(f"     -> {p.introduce()}")


def demo_interface(notifiables: List[INotifiable]) -> None:
    section("INTERFACE (INotifiable) — send_notification() แบบ polymorphic")
    msg = "ประชุมประจำเดือน วันนี้ 18:00 น. ณ ศาลาชุมชน"
    for obj in notifiables:
        print(f"  {obj.send_notification(msg)}")


def demo_access_modifier(r: Resident, a: Admin) -> None:
    section("ACCESS MODIFIER — public / protected / private")
    print(f"  Public    r.name          = {r.name}")
    print(f"  Protected r._age          = {r._age}")
    print(f"  Private   r.email (prop)  = {r.email}   <- เข้าผ่าน @property")
    print(f"  Class var Person.pop      = {Person.get_population()} คน")
    print()
    print(f"  ลองแก้ email ที่ถูกต้อง:")
    r.email = "somchai_new@email.com"
    print(f"  r.email หลังแก้ = {r.email}")
    print()
    print(f"  ลองแก้ email ผิดรูปแบบ → คาด ValueError:")
    try:
        r.email = "badformat"
    except ValueError as e:
        print(f"  ValueError: {e}")


def demo_overload_override(persons: List[Person],
                           r: Resident, a: Admin) -> None:
    section("OVERLOAD & OVERRIDE")

    print("  [Override] introduce() — แต่ละ class ให้ผลต่างกัน:")
    for p in persons:
        print(f"  ({type(p).__name__:15}) {p.introduce()}")

    print()
    print("  [Overload] report_issue() — ใช้ default parameters:")
    print(f"  -> {r.report_issue('น้ำไม่ไหล')}")
    print(f"  -> {r.report_issue('ไฟดับ', 'บริเวณซอย 3')}")
    print(f"  -> {r.report_issue('ขยะไม่ถูกเก็บ', 'หน้าบ้านเลขที่ 50', 'ด่วน')}")

    print()
    print("  [Overload] approve_request() — ใช้ default parameters:")
    print(f"  -> {a.approve_request(101)}")
    print(f"  -> {a.approve_request(102, 'ผ่านการตรวจสอบ')}")
    print(f"  -> {a.approve_request(103, 'รอเอกสาร', False)}")


def demo_encapsulation(r1: Resident, r2: Resident, head: VillageHead) -> None:
    section("ENCAPSULATION (ส่วน P ใน PIE) — ซ่อน state / จัดการผ่าน method")

    print("  [IPayable] ชำระค่าส่วนกลาง:")
    print(f"  -> {r1.pay(500)}")
    print(f"  -> {r2.pay(300)}")     # ไม่พอ
    print(f"  -> {head.pay(999)}")   # ยกเว้น

    print()
    print("  [Budget] ผู้ใหญ่บ้านจัดสรรงบ:")
    print(f"  -> {head.allocate_budget('ซ่อมถนนสายหลัก', 25_000)}")
    print(f"  -> {head.allocate_budget('ติดตั้งกล้อง CCTV', 40_000)}")
    print(f"  -> {head.allocate_budget('สร้างสนามเด็กเล่น', 90_000)}")  # เกิน


def demo_abstract_class() -> None:
    section("ABSTRACT CLASS — ไม่สามารถสร้าง instance โดยตรง")
    try:
        _ = Person("Test", 20, "t@t.com")   # type: ignore
    except TypeError as e:
        print(f"  TypeError: {e}")
    print("  => ต้อง subclass และ implement abstract methods ก่อน")


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print("\n" + "="*60)
    print("  OOP DEMO — ระบบจัดการชุมชน")
    print("  แสดง: PIE | Access Modifier | Overload&Override")
    print("        Abstract Class | Interface")
    print("="*60)

    # --- สร้าง object ---
    resident1 = Resident("สมชาย ใจดี",   35, "somchai@email.com",  "123/4", "หมู่บ้านสุขสันต์")
    resident2 = Resident("สมหญิง รักดี", 28, "somying@email.com",  "45/2",  "หมู่บ้านสุขสันต์")
    admin1    = Admin("วิชัย มั่นคง",    42, "wichai@admin.com",   "A001",  "ฝ่ายทะเบียน")
    head1     = VillageHead("ประยุทธ นำชัย", 55, "prayuth@village.com", "H001", "หมู่บ้านสุขสันต์")

    all_persons: List[Person]       = [resident1, resident2, admin1, head1]
    notifiables: List[INotifiable]  = [resident1, resident2, admin1, head1]

    # --- สาธิต ---
    demo_polymorphism(all_persons)
    demo_interface(notifiables)
    demo_access_modifier(resident1, admin1)
    demo_overload_override(all_persons, resident1, admin1)
    demo_encapsulation(resident1, resident2, head1)
    demo_abstract_class()

    section("จบการสาธิต")


if __name__ == "__main__":
    main()
