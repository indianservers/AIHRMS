from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.crud.base import CRUDBase
from app.models.attendance import Attendance, AttendanceRegularization, Holiday, Shift, OvertimeRequest


class CRUDAttendance(CRUDBase):
    def __init__(self):
        super().__init__(Attendance)

    def get_today(self, db: Session, employee_id: int) -> Optional[Attendance]:
        today = date.today()
        return (
            db.query(Attendance)
            .filter(and_(Attendance.employee_id == employee_id, Attendance.attendance_date == today))
            .first()
        )

    def check_in(self, db: Session, employee_id: int, location: str = None, ip: str = None, source: str = "Web") -> Attendance:
        today = date.today()
        existing = self.get_today(db, employee_id)
        now = datetime.now(timezone.utc)

        if existing:
            if not existing.check_in:
                existing.check_in = now
                existing.check_in_location = location
                existing.check_in_ip = ip
                existing.status = "Present"
                db.commit()
                db.refresh(existing)
            return existing

        record = Attendance(
            employee_id=employee_id,
            attendance_date=today,
            check_in=now,
            check_in_location=location,
            check_in_ip=ip,
            source=source,
            status="Present",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def check_out(self, db: Session, employee_id: int, location: str = None, ip: str = None) -> Optional[Attendance]:
        record = self.get_today(db, employee_id)
        if not record or not record.check_in:
            return None

        now = datetime.now(timezone.utc)
        record.check_out = now
        record.check_out_location = location
        record.check_out_ip = ip

        # Calculate hours
        diff = now - record.check_in
        total_hours = Decimal(str(round(diff.total_seconds() / 3600, 2)))
        record.total_hours = total_hours

        standard_hours = Decimal("8.0")
        if total_hours > standard_hours:
            record.overtime_hours = total_hours - standard_hours

        db.commit()
        db.refresh(record)
        return record

    def get_employee_attendance(
        self, db: Session, employee_id: int, from_date: date, to_date: date
    ) -> List[Attendance]:
        return (
            db.query(Attendance)
            .filter(
                and_(
                    Attendance.employee_id == employee_id,
                    Attendance.attendance_date >= from_date,
                    Attendance.attendance_date <= to_date,
                )
            )
            .order_by(Attendance.attendance_date.desc())
            .all()
        )

    def get_monthly_summary(self, db: Session, employee_id: int, month: int, year: int) -> dict:
        from_date = date(year, month, 1)
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        to_date = date(year, month, last_day)

        records = self.get_employee_attendance(db, employee_id, from_date, to_date)
        status_counts = {}
        total_hours = Decimal("0")
        overtime_hours = Decimal("0")

        for r in records:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1
            if r.total_hours:
                total_hours += r.total_hours
            if r.overtime_hours:
                overtime_hours += r.overtime_hours

        return {
            "employee_id": employee_id,
            "month": month,
            "year": year,
            "total_records": len(records),
            "present": status_counts.get("Present", 0),
            "absent": status_counts.get("Absent", 0),
            "half_day": status_counts.get("Half-day", 0),
            "wfh": status_counts.get("WFH", 0),
            "total_hours": float(total_hours),
            "overtime_hours": float(overtime_hours),
            "status_breakdown": status_counts,
        }

    def get_team_attendance(self, db: Session, manager_employee_id: int, attendance_date: date) -> List[dict]:
        from app.models.employee import Employee
        team = db.query(Employee).filter(Employee.reporting_manager_id == manager_employee_id).all()
        result = []
        for emp in team:
            att = (
                db.query(Attendance)
                .filter(and_(Attendance.employee_id == emp.id, Attendance.attendance_date == attendance_date))
                .first()
            )
            result.append({
                "employee_id": emp.id,
                "employee_name": f"{emp.first_name} {emp.last_name}",
                "status": att.status if att else "Absent",
                "check_in": att.check_in if att else None,
                "check_out": att.check_out if att else None,
            })
        return result


class CRUDHoliday(CRUDBase):
    def __init__(self):
        super().__init__(Holiday)

    def get_upcoming(self, db: Session, limit: int = 10) -> List[Holiday]:
        today = date.today()
        return (
            db.query(Holiday)
            .filter(and_(Holiday.holiday_date >= today, Holiday.is_active == True))
            .order_by(Holiday.holiday_date)
            .limit(limit)
            .all()
        )

    def is_holiday(self, db: Session, check_date: date) -> bool:
        return db.query(Holiday).filter(
            and_(Holiday.holiday_date == check_date, Holiday.is_active == True)
        ).count() > 0


crud_attendance = CRUDAttendance()
crud_holiday = CRUDHoliday()
