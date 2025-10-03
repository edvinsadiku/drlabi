from datetime import datetime, date, time, timedelta
from decimal import Decimal, InvalidOperation
import json

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models, transaction
from django.db.models import (
    Q, F, Value, Case, When, ExpressionWrapper, Sum,
    Count, OuterRef, Subquery, DecimalField, DateTimeField, Max
)
from django.db.models.functions import Coalesce, Greatest
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import (
    Patient, Historia, HistoryOrtodentics, PatienOrtodentics,
    PatientDocument, Appointment, Shpenzimet,
    CareHistory, Agreement, Payment
)

@login_required
def home(request):
    return patient_list(request)


def patient_list(request):
    q = (request.GET.get("q") or "").strip()

    qs = Patient.objects.all()

    # Search
    if q:
        qs = qs.filter(
            Q(emri_mbiemri__icontains=q) |
            Q(telefoni__icontains=q) |
            Q(emaili__icontains=q)
        )

    # ---- Lightweight annotations ----
    qs = qs.annotate(
        historias_count=Count("historias"),
        last_historia=Max("historias__created_at"),
    ).annotate(
        last_history=Coalesce(
            F("last_historia"),
            Value(None, output_field=DateTimeField())
        ),
        register_date=F("created_at"),
        city=Coalesce(F("adresa"), Value("", output_field=None)),
    )

    # Sorting default: nga historia e fundit
    qs = qs.order_by("-last_history", "-id")

    # Pagination
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    current = page_obj.number
    total_pages = paginator.num_pages
    start = max(1, current - 2)
    end = min(total_pages, current + 2)
    page_numbers = range(start, end + 1)

    return render(request, "clinic/patient_list.html", {
        "page_obj": page_obj,
        "page_numbers": page_numbers,
        "q": q,
        "total_patients": paginator.count,
    })



@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    # ---------- LEGACY ----------
    historias = patient.historias.order_by("-id")

    ortho_histories = HistoryOrtodentics.objects.filter(
        emri_i_pacientit=patient.emri_mbiemri
    ).order_by("-id")

    total_vlera  = sum((h.vlera  or Decimal("0")) for h in historias)
    total_paguar = sum((h.paguar or Decimal("0")) for h in historias)
    total_borgji = sum((h.borgji or Decimal("0")) for h in historias)

    # ---------- SISTEMI I RI ----------
    DECIMAL = DecimalField(max_digits=18, decimal_places=2)
    ZERO = Value(Decimal("0.00"), output_field=DECIMAL)

    # Pagesat
    payments_new_qs = (
        Payment.objects.filter(patient=patient)
        .select_related("history", "agreement", "created_by")
        .order_by("-id")
    )
    total_paid_new = payments_new_qs.aggregate(
        s=Coalesce(Sum("amount"), ZERO, output_field=DECIMAL)
    )["s"]

    # Histori të reja
    care_qs_base = CareHistory.objects.filter(patient=patient).select_related("agreement", "created_by")

    care_histories_all = (
        care_qs_base
        .annotate(
            paid_sum=Coalesce(Sum("payments__amount"), ZERO, output_field=DECIMAL)
        )
        .annotate(
            debt_raw=ExpressionWrapper(
                Coalesce(F("amount"), ZERO, output_field=DECIMAL) - F("paid_sum"),
                output_field=DECIMAL,
            )
        )
        .annotate(
            debt_sum=Case(
                When(included_in_agreement=True, then=ZERO),
                default=F("debt_raw"),
                output_field=DECIMAL,
            )
        )
        .order_by("-date", "-id")
    )

    care_total_non_agreement = (
        care_qs_base
        .filter(agreement__isnull=True, included_in_agreement=False)
        .aggregate(s=Coalesce(Sum("amount"), ZERO, output_field=DECIMAL))
    )["s"]

    unpaid_histories = (
        care_qs_base
        .annotate(paid_sum=Coalesce(Sum("payments__amount"), ZERO, output_field=DECIMAL))
        .annotate(
            debt_sum=ExpressionWrapper(
                Coalesce(F("amount"), ZERO, output_field=DECIMAL) - F("paid_sum"),
                output_field=DECIMAL,
            )
        )
        .filter(agreement__isnull=True, included_in_agreement=False, debt_sum__gt=0)
        .order_by("date", "id")
    )

    agreements_qs = (
        Agreement.objects.filter(patient=patient)
        .annotate(paid_sum=Coalesce(Sum("payments__amount"), ZERO, output_field=DECIMAL))
        .annotate(bal_sum=ExpressionWrapper(F("total_amount") - F("paid_sum"), output_field=DECIMAL))
        .order_by("-id")
    )
    agreements_active = agreements_qs.filter(status="active")

    agreements_total_amount = agreements_qs.aggregate(
        s=Coalesce(Sum("total_amount"), ZERO, output_field=DECIMAL)
    )["s"]

    total_agreements_balance = sum((a.bal_sum for a in agreements_active), Decimal("0.00"))
    if total_agreements_balance < 0:
        total_agreements_balance = Decimal("0.00")

    total_billed_new = (care_total_non_agreement or Decimal("0.00")) + (agreements_total_amount or Decimal("0.00"))

    debt_new = total_billed_new - (total_paid_new or Decimal("0.00"))
    if debt_new < 0:
        debt_new = Decimal("0.00")

    # ---------- DOKUMENTET ----------
    documents = PatientDocument.objects.filter(patient=patient).select_related("uploaded_by").order_by("-uploaded_at")

    return render(request, "clinic/patient_detail.html", {
        "patient": patient,
        "historias": historias,
        "ortho_histories": ortho_histories,
        "total_vlera": total_vlera,
        "total_paguar": total_paguar,
        "total_borgji": total_borgji,
        "payments_new": payments_new_qs,
        "total_paid_new": total_paid_new,
        "total_billed_new": total_billed_new,
        "debt_new": debt_new,
        "total_agreements_balance": total_agreements_balance,
        "agreements_new": agreements_qs,
        "agreements_active": agreements_active,
        "care_histories_all": care_histories_all,
        "unpaid_histories": unpaid_histories,
        "documents": documents,   # 📌 e dërgojmë tek template
    })

@login_required
def history_detail(request, pk):
    history = get_object_or_404(Historia, pk=pk)  # ose Historia nëse modeli quhet ndryshe
    return render(request, "clinic/history_detail.html", {
        "history": history,
    })



# -------------------- ORTO --------------------
@login_required
def orto_patient_list(request):
    q = (request.GET.get("q") or "").strip()
    patients = PatienOrtodentics.objects.all()
    if q:
        patients = patients.filter(
            models.Q(emri_mbiemri__icontains=q) |
            models.Q(telefoni__icontains=q) |
            models.Q(emaili__icontains=q)
        )
    patients = patients.order_by("-id")
    return render(request, "clinic/orto_patient_list.html", {"patients": patients, "q": q})

@login_required
def orto_patient_detail(request, pk):
    p = get_object_or_404(PatienOrtodentics, pk=pk)
    return render(request, "clinic/orto_patient_detail.html", {"patient": p})


# -------------------- ADD HISTORY (pa forms) --------------------
def _to_decimal(val):
    if val in (None, "", "None"):
        return None
    try:
        return Decimal(str(val).replace(",", "."))
    except InvalidOperation:
        return None



def _parse_date_any(value):
    """Kthen datetime.date nga string 'YYYY-MM-DD' ose 'dd.mm.yyyy'. Default: sot."""
    if not value:
        return now().date()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except Exception:
            pass
    return now().date()

@login_required
def add_history(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == "POST":
        # --- DATA ---
        data_raw = request.POST.get("data")
        date_obj = _parse_date_any(data_raw)

        # --- FUSHA TË TJERA ---
        dhembi   = request.POST.get("dhembi") or None
        diagnoza = request.POST.get("diagnoza") or None
        trajtimi = request.POST.get("trajtimi") or None
        vlera    = _to_decimal(request.POST.get("vlera"))
        paguar   = _to_decimal(request.POST.get("paguar"))
        borgji   = _to_decimal(request.POST.get("borgji"))
        doctor   = request.POST.get("doctor") or None
        pasqyra  = request.POST.get("pasqyra_e_dhembit") or None
        punim    = request.POST.get("punim_protetikor") or None
        tekniku  = request.POST.get("tekniku") or None
        verejtje = request.POST.get("verejtje") or None

        # --- MARRËVESHJE ---
        agreement_id = request.POST.get("agreement_id") or None
        included = False
        agreement = None

        if agreement_id and str(agreement_id).isdigit():
            agreement = Agreement.objects.filter(
                id=int(agreement_id), patient=patient, status="active"
            ).first()
            if agreement:
                included = True  # automatikisht e përfshirë në marrëveshje

        # --- VALIDIMI: nëse nuk ka marrëveshje, vlera është e detyrueshme
        if not agreement and (not vlera or vlera <= 0):
            messages.error(request, "Ju lutem shënoni vlerën e shërbimit ose zgjidhni një marrëveshje.")
            return redirect("add_history", pk=patient.pk)

        # 1) KRIJO CareHistory
        ch = CareHistory.objects.create(
            patient=patient,
            date=date_obj,
            tooth=dhembi,
            diagnosis=diagnoza,
            treatment=trajtimi,
            amount=(None if included else vlera),
            notes=verejtje,
            doctor=doctor,
            agreement=(agreement if included else None),
            included_in_agreement=included,
            created_by=request.user,
            updated_by=request.user,
        )

        # 2) Nëse ka pagesë → fut Payment
        if (paguar or Decimal("0")) > 0 and not included:
            Payment.objects.create(
                patient=patient,
                amount=paguar,
                method="cash",
                history=ch,
                notes="Pagesë nga forma e re",
                created_by=request.user,
                updated_by=request.user,
            )

        return redirect("patient_detail", pk=patient.pk)

    return render(request, "clinic/history_form_simple.html", {
        "patient": patient,
        "today": now().date(),
        "agreements": patient.agreements.filter(status="active").order_by("-created_at"),
    })

@login_required
def history_detail(request, pk):
    history = get_object_or_404(Historia, pk=pk)
    return render(request, "clinic/history_detail.html", {"history": history})

@login_required
def add_orto_history(request, pk):
    """
    Shton një rekord të ri në HistoryOrtodentics për një PatienOrtodentics (pa ModelForm).
    """
    patient_orto = get_object_or_404(PatienOrtodentics, pk=pk)

    if request.method == "POST":
        data = request.POST.get("data") or None
        diagnoza = request.POST.get("diagnoza") or None
        trajtimi = request.POST.get("trajtimi") or None
        vlera = _to_decimal(request.POST.get("vlera"))
        paguar = _to_decimal(request.POST.get("paguar"))
        borgji = _to_decimal(request.POST.get("borgji"))
        doctor = request.POST.get("doctor") or None
        verejtje = request.POST.get("verejtje") or None

        obj = HistoryOrtodentics(
            data=data,
            diagnoza=diagnoza,
            trajtimi=trajtimi,
            vlera=vlera,
            paguar=paguar,
            borgji=borgji,
            doctor=doctor,
            verejtje=verejtje,
        )
        # ⚠️ LIDHJA ME PACIENTIN ORTO – NDRYSHO EMRIN E FUSHËS NËSE ËSHTË NDRYSHE
        obj.patien_ortodentics = patient_orto
        obj.save()

        return redirect("orto_patient_detail", pk=patient_orto.pk)

    return render(request, "clinic/orto_history_form_simple.html", {
        "patient": patient_orto
    })

@login_required
def edit_history(request, pk):
    historia = get_object_or_404(Historia, pk=pk)
    patient = historia.patient

    if request.method == "POST":
        historia.data = request.POST.get("data") or now().date()
        historia.doctor = request.POST.get("doctor") or None
        historia.dhembi = request.POST.get("dhembi") or None
        historia.diagnoza = request.POST.get("diagnoza") or None
        historia.trajtimi = request.POST.get("trajtimi") or None
        historia.vlera = _to_decimal(request.POST.get("vlera"))
        historia.paguar = _to_decimal(request.POST.get("paguar"))
        historia.borgji = _to_decimal(request.POST.get("borgji"))
        historia.pasqyra_e_dhembit = request.POST.get("pasqyra_e_dhembit") or None
        historia.tekniku = request.POST.get("tekniku") or None
        historia.punim_protetikor = request.POST.get("punim_protetikor") or None
        historia.verejtje = request.POST.get("verejtje") or None
        historia.save()
        return redirect("patient_detail", pk=patient.pk)

    return render(request, "clinic/history_form_simple.html", {
        "patient": patient,
        "historia": historia,
        "today": now().date(),  # përdoret vetëm kur s’ka data
    })


@login_required
def delete_history(request, pk):
    historia = get_object_or_404(Historia, pk=pk)
    patient_id = historia.patient.pk

    if request.method == "POST":
        historia.delete()
        return redirect("patient_detail", pk=patient_id)

    return render(request, "clinic/history_confirm_delete.html", {
        "historia": historia
    })


def _num(x):
    if x in (None, "", "None"):
        return 0
    try:
        return float(x)
    except Exception:
        return 0


def _parse_ddmmyyyy(s: str):
    try:
        return datetime.strptime(s.strip(), "%d.%m.%Y").date()
    except Exception:
        return None

def _dec(x):
    if x in (None, "", "None"):
        return Decimal("0")
    try:
        return Decimal(str(x).replace(",", "."))
    except (InvalidOperation, Exception):
        return Decimal("0")


@login_required
def reports(request):
    """
    Raport dinamik me filtra:
      mode = day | week | month | year
      order = desc | asc   (renditja sipas datës)
      day   = YYYY-MM-DD
      week  = YYYY-Www (input type="week")
      month = YYYY-MM   (input type="month")
      year  = YYYY
    """
    mode  = (request.GET.get("mode") or "day").lower()
    if mode not in {"day", "week", "month", "year"}:
        mode = "day"

    order = (request.GET.get("order") or "desc").lower()
    if order not in {"asc", "desc"}:
        order = "desc"

    today = now().date()

    # Lexo target-in sipas modit, me default-e të mençura
    if mode == "day":
        day_str = request.GET.get("day")
        target_day = datetime.strptime(day_str, "%Y-%m-%d").date() if day_str else today

        # Prefiltro në DB vetëm për vitin target (shpejtësi)
        qs = Historia.objects.filter(data__endswith=f".{target_day.year}").select_related("patient")

        items = []
        for h in qs:
            d = _parse_ddmmyyyy(h.data or "")
            if d == target_day:
                items.append({
                    "obj": h,
                    "d": d,
                    "emri": getattr(h.patient, "emri_mbiemri", ""),
                    "vlera": _dec(h.vlera),
                    "paguar": _dec(h.paguar),
                    "borgji": _dec(h.borgji),
                })

    elif mode == "week":
        # Preferojmë input type="week"
        week_str = request.GET.get("week")  # p.sh. "2025-W35"
        if week_str:
            y, w = week_str.split("-W")
            y, w = int(y), int(w)
            # ISO week → e hëna:
            week_start = date.fromisocalendar(y, w, 1)
        else:
            # default: java e sotme
            y, w, _ = today.isocalendar()
            week_start = date.fromisocalendar(y, w, 1)

        week_end = week_start + timedelta(days=6)

        # Prefiltro për vitet e mundshme (java mund të bjerë në dy vite)
        years = {week_start.year, week_end.year}
        q = Q()
        for yr in years:
            q |= Q(data__endswith=f".{yr}")
        qs = Historia.objects.filter(q).select_related("patient")

        items = []
        for h in qs:
            d = _parse_ddmmyyyy(h.data or "")
            if d and week_start <= d <= week_end:
                items.append({
                    "obj": h,
                    "d": d,
                    "emri": getattr(h.patient, "emri_mbiemri", ""),
                    "vlera": _dec(h.vlera),
                    "paguar": _dec(h.paguar),
                    "borgji": _dec(h.borgji),
                })

    elif mode == "month":
        month_str = request.GET.get("month")  # "YYYY-MM"
        if month_str:
            y, m = month_str.split("-")
            y, m = int(y), int(m)
        else:
            y, m = today.year, today.month

        # Prefiltro: ".MM.YYYY" brenda stringut p.sh. ".08.2025"
        mm = f"{m:02d}"
        qs = Historia.objects.filter(data__contains=f".{mm}.{y}").select_related("patient")

        items = []
        for h in qs:
            d = _parse_ddmmyyyy(h.data or "")
            if d and d.year == y and d.month == m:
                items.append({
                    "obj": h,
                    "d": d,
                    "emri": getattr(h.patient, "emri_mbiemri", ""),
                    "vlera": _dec(h.vlera),
                    "paguar": _dec(h.paguar),
                    "borgji": _dec(h.borgji),
                })

    else:  # year
        year_str = request.GET.get("year")
        y = int(year_str) if (year_str and year_str.isdigit()) else today.year

        qs = Historia.objects.filter(data__endswith=f".{y}").select_related("patient")

        items = []
        for h in qs:
            d = _parse_ddmmyyyy(h.data or "")
            if d and d.year == y:
                items.append({
                    "obj": h,
                    "d": d,
                    "emri": getattr(h.patient, "emri_mbiemri", ""),
                    "vlera": _dec(h.vlera),
                    "paguar": _dec(h.paguar),
                    "borgji": _dec(h.borgji),
                })

    # Renditja sipas datës
    reverse = (order == "desc")
    items.sort(key=lambda r: (r["d"] or date.min, r["obj"].id or 0), reverse=reverse)

    # Totale
    total_vlera  = sum((r["vlera"]  for r in items), Decimal("0"))
    total_paguar = sum((r["paguar"] for r in items), Decimal("0"))
    total_borgji = sum((r["borgji"] for r in items), Decimal("0"))

    # Lista viteve për dropdown (opsionale)
    # mund të nxjerrim nga DB, por për thjeshtësi përdorim disa vite afër sotit
    years = list(range(today.year, today.year - 10, -1))

    ctx = {
        "mode": mode,
        "order": order,
        "items": items,
        "total_vlera": total_vlera,
        "total_paguar": total_paguar,
        "total_borgji": total_borgji,
        "today": today,
        "years": years,
        # vlera të rikthyera në UI
        "picked_day":  request.GET.get("day") or today.strftime("%Y-%m-%d"),
        "picked_week": request.GET.get("week") or f"{today.isocalendar().year}-W{today.isocalendar().week:02d}",
        "picked_month": request.GET.get("month") or today.strftime("%Y-%m"),
        "picked_year": request.GET.get("year") or str(today.year),
    }
    return render(request, "clinic/reports.html", ctx)

from django.contrib import messages
@login_required
def add_or_edit_patient(request, pk=None):
    patient = None
    if pk:
        patient = get_object_or_404(Patient, pk=pk)

    if request.method == "POST":
        emri_mbiemri = request.POST.get("emri_mbiemri")
        data_e_lindjes = request.POST.get("data_e_lindjes") or None
        telefoni = request.POST.get("telefoni")
        emaili = request.POST.get("emaili")
        leternjoftimi = request.POST.get("leternjoftimi")

        if not emri_mbiemri:
            messages.error(request, "Ju lutem plotësoni emrin e pacientit.")
        else:
            if patient:  # EDIT
                patient.emri_mbiemri = emri_mbiemri
                patient.data_e_lindjes = data_e_lindjes
                patient.telefoni = telefoni
                patient.emaili = emaili
                patient.leternjoftimi = leternjoftimi
                patient.save()
                messages.success(request, f"Pacienti {patient.emri_mbiemri} u përditësua me sukses.")
            else:  # CREATE
                patient = Patient.objects.create(
                    emri_mbiemri=emri_mbiemri,
                    data_e_lindjes=data_e_lindjes,
                    telefoni=telefoni,
                    emaili=emaili,
                    leternjoftimi=leternjoftimi
                )
                messages.success(request, f"Pacienti {patient.emri_mbiemri} (ID: {patient.id}) u shtua me sukses.")

            return redirect("patient_list")

    return render(request, "clinic/add_patient.html", {"patient": patient})

@login_required
def shpenzime_list(request):
    shpenzime = Shpenzimet.objects.all().order_by("-muaji")
    total = sum(s.vlera or 0 for s in shpenzime)
    return render(request, "clinic/shpenzime_list.html", {
        "shpenzime": shpenzime,
        "total": total,
    })

@login_required
def shpenzime_add(request):
    if request.method == "POST":
        shpenzimi = request.POST.get("shpenzimi")
        muaji = request.POST.get("muaji") or None
        vlera = request.POST.get("vlera") or None
        paguar = bool(request.POST.get("paguar"))
        pershkrimi = request.POST.get("pershkrimi")

        Shpenzimet.objects.create(
            shpenzimi=shpenzimi,
            muaji=muaji,
            vlera=vlera,
            paguar=paguar,
            pershkrimi=pershkrimi,
            created_at=now(),
            updated_at=now(),
        )
        return redirect("shpenzime_list")

    return render(request, "clinic/shpenzime_form.html")


@login_required
def shpenzime_delete(request, pk):
    s = get_object_or_404(Shpenzimet, pk=pk)
    if request.method == "POST":
        s.delete()
        return redirect("shpenzime_list")
    return render(request, "clinic/shpenzime_confirm_delete.html", {"shpenzim": s})



def appointments_calendar(request):
    patients = Patient.objects.all().order_by("emri_mbiemri")
    return render(request, "clinic/appointments_calendar.html", {"patients": patients})



def appointments_events(request):
    doctor = request.GET.get("doctor")
    qs = Appointment.objects.select_related("patient")
    if doctor:
        qs = qs.filter(doctor=doctor)

    events = []
    for appt in qs:
        events.append({
            "id": appt.id,
            "title": f"{appt.patient.emri_mbiemri} – {appt.title} ({appt.doctor})",
            "start": appt.start.isoformat(),
            "end": appt.end.isoformat() if appt.end else None,
            "patient_id": appt.patient.id,
            "doctor": appt.doctor,
            "status": appt.status,
            "notes": appt.notes,
        })
    return JsonResponse(events, safe=False)

@csrf_exempt
def appointments_create(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # ⚡ tani merret pacienti nga request
        patient_id = data.get("patient")
        patient = get_object_or_404(Patient, pk=patient_id)

        appt = Appointment.objects.create(
            patient=patient,
            doctor=data.get("doctor"),
            title=data.get("title", "Takim"),
            start=data.get("start", now()),
            end=data.get("end"),
            status=data.get("status", "scheduled"),
            notes=data.get("notes", ""),
        )
        return JsonResponse({"id": appt.id})
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def appointments_update(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        data = json.loads(request.body)

        if data.get("patient"):
            appt.patient = get_object_or_404(Patient, pk=data["patient"])
        if data.get("doctor"):
            appt.doctor = data["doctor"]
        if data.get("title"):
            appt.title = data["title"]
        if data.get("start"):
            appt.start = data["start"]
        if "end" in data:
            appt.end = data["end"] or None
        if data.get("status"):
            appt.status = data["status"]
        if "notes" in data:
            appt.notes = data["notes"]

        appt.save()
        return JsonResponse({"status": "updated"})
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def appointments_delete(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        appt.delete()
        return JsonResponse({"status": "deleted"})
    return JsonResponse({"error": "Invalid request"}, status=400)
    

@login_required
@require_POST
def add_payment(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    amount = _to_decimal(request.POST.get("amount"))
    method = request.POST.get("method") or "cash"
    notes  = request.POST.get("notes") or ""

    # mund të vijë nga forma e vjetër (history_id) ose e re (history_ids[])
    history_ids = request.POST.getlist("history_ids") or request.POST.getlist("history_id")
    agreement_id = request.POST.get("agreement_id") or ""

    # Validime bazë
    if not amount or amount <= 0:
        messages.error(request, "Shuma e pagesës nuk është e vlefshme.")
        return redirect("patient_detail", pk=patient.pk)

    if agreement_id and history_ids:
        messages.error(request, "Zgjidh ose një marrëveshje ose disa histori — jo të dyja.")
        return redirect("patient_detail", pk=patient.pk)

    # --- Rast 1: Pagesë për MARRËVESHJE ---
    if agreement_id:
        agreement = get_object_or_404(Agreement, pk=int(agreement_id), patient=patient, status="active")
        Payment.objects.create(
            patient=patient,
            amount=amount,
            method=method,
            notes=notes,
            agreement=agreement,
            created_by=request.user,
        )
        messages.success(request, f"Pagesa {amount}€ u shtua për marrëveshjen “{agreement.title}”.")
        return redirect("patient_detail", pk=patient.pk)

    # --- Rast 2: Pagesë për NJË ose DISA HISTORI ---
    if not history_ids:
        messages.error(request, "Zgjidh të paktën një histori ose një marrëveshje.")
        return redirect("patient_detail", pk=patient.pk)

    # Merr historitë e zgjedhura (vetëm jashtë marrëveshjeve)
    histories = (
        CareHistory.objects
        .filter(id__in=[int(x) for x in history_ids], patient=patient, agreement__isnull=True, included_in_agreement=False)
        .order_by("date", "id")   # aloko nga më e vjetra te më e reja
    )
    if not histories.exists():
        messages.error(request, "Asnjë nga historitë e zgjedhura nuk është e vlefshme për pagesë.")
        return redirect("patient_detail", pk=patient.pk)

    # Llogarit borxhin e secilës histori: amount - sum(payments)
    def history_outstanding(h: CareHistory) -> Decimal:
        if not h.amount:
            return Decimal("0")
        paid = Payment.objects.filter(history=h).aggregate(
            s=Coalesce(Sum("amount"), Value(0), output_field=DecimalField(max_digits=18, decimal_places=2))
        )["s"] or Decimal("0")
        due = Decimal(h.amount) - paid
        return due if due > 0 else Decimal("0")

    remaining = Decimal(amount)
    created_count = 0
    breakdown = []

    with transaction.atomic():
        for h in histories:
            if remaining <= 0:
                break
            due = history_outstanding(h)
            if due <= 0:
                continue
            pay_part = due if remaining >= due else remaining
            if pay_part > 0:
                Payment.objects.create(
                    patient=patient,
                    amount=pay_part,
                    method=method,
                    notes=notes,
                    history=h,
                    created_by=request.user,
                )
                created_count += 1
                breakdown.append(f"{h.diagnosis or 'Histori'}: {pay_part}€")
                remaining -= pay_part

    if created_count == 0:
        messages.info(request, "Histori të zgjedhura nuk kishin borxh. Asnjë pagesë nuk u krijua.")
    else:
        msg = f"Krijuar {created_count} pagesa për {amount - remaining:.2f}€."
        if remaining > 0:
            msg += f" {remaining:.2f}€ mbetën të pa-alokuara (nuk kishte më borxh)."
        if breakdown:
            msg += " Detaje: " + "; ".join(breakdown)
        messages.success(request, msg)

    return redirect("patient_detail", pk=patient.pk)

@login_required
def agreement_create(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        title        = request.POST.get("title") or "Marrëveshje trajtimi"
        total_amount = _to_decimal(request.POST.get("total_amount")) or Decimal("0")
        start_date   = request.POST.get("start_date") or None
        end_date     = request.POST.get("end_date") or None
        doctor       = request.POST.get("doctor") or None   # 👉 merr doktorin
        notes        = request.POST.get("notes") or ""
        status       = request.POST.get("status") or "active"

        Agreement.objects.create(
            patient=patient,
            title=title,
            total_amount=total_amount,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            status=status,
            doctor=doctor,   # 👉 ruaj doktorin
            created_by=request.user,
            updated_by=request.user,
        )
        return redirect("patient_detail", pk=patient.pk)
    return render(request, "clinic/agreement_form.html", {"patient": patient})


@login_required
def agreement_close(request, agreement_id):
    # Marrëveshja + total i paguar deri tani
    agreement = (
        Agreement.objects
        .filter(pk=agreement_id)
        .annotate(
            paid_sum=Coalesce(
                Sum("payments__amount"),
                Value(0),
                output_field=DecimalField(max_digits=18, decimal_places=2),
            )
        )
        .select_related("patient")
        .first()
    )
    if not agreement:
        raise Http404

    if agreement.status != "active":
        messages.info(request, "Kjo marrëveshje nuk është aktive.")
        return redirect("patient_detail", pk=agreement.patient_id)

    # Sa mbetet për t'u paguar
    outstanding = (agreement.total_amount or Decimal("0")) - (agreement.paid_sum or Decimal("0"))

    if outstanding > Decimal("0.00"):
        messages.error(
            request,
            f"Nuk mund të mbyllet: mbeten {outstanding}€ për t’u paguar."
        )
        return redirect("patient_detail", pk=agreement.patient_id)

    # OK — e mbyllim
    agreement.status = "closed"
    agreement.updated_by = request.user
    agreement.updated_at = now()
    agreement.save(update_fields=["status", "updated_by", "updated_at"])

    messages.success(request, "Marrëveshja u mbyll me sukses.")
    return redirect("patient_detail", pk=agreement.patient_id)


# ---------------- HELPER ----------------
def _period_range(request):
    mode = (request.GET.get("mode") or "day").lower()
    today = datetime.now().date()

    if mode == "day":
        d_str = request.GET.get("day")
        d = datetime.strptime(d_str, "%Y-%m-%d").date() if d_str else today
        return d, d

    if mode == "week":
        w_str = request.GET.get("week")
        if w_str:
            y, w = w_str.split("-W")
            start = date.fromisocalendar(int(y), int(w), 1)
        else:
            y, w, _ = today.isocalendar()
            start = date.fromisocalendar(y, w, 1)
        end = start + timedelta(days=6)
        return start, end

    if mode == "month":
        m_str = request.GET.get("month")
        if m_str:
            y, m = m_str.split("-")
            y, m = int(y), int(m)
        else:
            y, m = today.year, today.month
        start = date(y, m, 1)
        if m == 12:
            end = date(y, 12, 31)
        else:
            end = date(y, m + 1, 1) - timedelta(days=1)
        return start, end

    # year
    y_str = request.GET.get("year")
    y = int(y_str) if (y_str and y_str.isdigit()) else today.year
    return date(y, 1, 1), date(y, 12, 31)


def _obj_date(obj):
    """Gjithmonë kthen datetime për sortim."""
    if hasattr(obj, "date") and obj.date:  # CareHistory
        return datetime.combine(obj.date, datetime.min.time())
    if hasattr(obj, "created_at") and obj.created_at:  # Agreement / Payment
        return obj.created_at
    return datetime.min


# ---------------- MAIN REPORT VIEW ----------------
@login_required
def reports_new(request):
    start_date, end_date = _period_range(request)
    order = (request.GET.get("order") or "desc").lower()

    mode = (request.GET.get("mode") or "day").lower()
    picked_day = request.GET.get("day") or start_date.strftime("%Y-%m-%d")
    picked_week = request.GET.get("week") or f"{start_date.isocalendar()[0]}-W{start_date.isocalendar()[1]:02d}"
    picked_month = request.GET.get("month") or start_date.strftime("%Y-%m")
    picked_year = request.GET.get("year") or str(start_date.year)

    DECIMAL = DecimalField(max_digits=18, decimal_places=2)
    ZERO = Value(Decimal("0.00"), output_field=DECIMAL)

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    # CARE HISTORIES
    payments_subq = (
        Payment.objects
        .filter(history=OuterRef("pk"))
        .values("history")
        .annotate(total=Sum("amount"))
        .values("total")[:1]
    )

    care_qs_all = (
        CareHistory.objects
        .select_related("patient")
        .filter(date__gte=start_date, date__lte=end_date)
        .annotate(paid_sum=Coalesce(Subquery(payments_subq, output_field=DECIMAL), ZERO))
    )

    # AGREEMENTS
    agreements_qs = (
        Agreement.objects
        .filter(created_at__date__lte=end_date)
        .annotate(paid_sum=Coalesce(Sum("payments__amount"), ZERO, output_field=DECIMAL))
    )

    # PAGESA SIPAS DOKTORIT (nga histori)
    payments_by_doctor = (
        Payment.objects
        .filter(created_at__gte=start_datetime, created_at__lte=end_datetime, history__isnull=False)
        .values(doctor_name=F("history__doctor"))
        .annotate(total=Coalesce(Sum("amount"), ZERO, output_field=DECIMAL))
        .order_by("-total")
    )

    # PAGESA SIPAS DOKTORIT (nga marrëveshje)
    payments_agreements = (
        Payment.objects
        .filter(created_at__gte=start_datetime, created_at__lte=end_datetime, agreement__isnull=False)
        .values(doctor_name=F("agreement__doctor"))
        .annotate(total=Coalesce(Sum("amount"), ZERO, output_field=DECIMAL))
    )

    # Kombino histori + marrëveshje
    payments_by_doctor_total = {}
    for p in payments_by_doctor:
        payments_by_doctor_total[p["doctor_name"]] = {
            "from_histories": p["total"] or Decimal("0.00"),
            "from_agreements": Decimal("0.00"),
        }

    for p in payments_agreements:
        if p["doctor_name"] not in payments_by_doctor_total:
            payments_by_doctor_total[p["doctor_name"]] = {
                "from_histories": Decimal("0.00"),
                "from_agreements": Decimal("0.00"),
            }
        payments_by_doctor_total[p["doctor_name"]]["from_agreements"] = p["total"] or Decimal("0.00")

    for doc, vals in payments_by_doctor_total.items():
        vals["total"] = (vals["from_histories"] or Decimal("0.00")) + (vals["from_agreements"] or Decimal("0.00"))

    # TOTAL KPI
    total_billed_histories = care_qs_all.filter(
        agreement__isnull=True, included_in_agreement=False
    ).aggregate(t=Coalesce(Sum("amount"), ZERO, output_field=DECIMAL))["t"]

    billed_agreements = Payment.objects.filter(
        agreement__isnull=False, created_at__gte=start_datetime, created_at__lte=end_datetime
    ).aggregate(t=Coalesce(Sum("amount"), ZERO, output_field=DECIMAL))["t"]

    total_billed = (total_billed_histories or Decimal("0")) + (billed_agreements or Decimal("0"))

    paid_histories = Payment.objects.filter(
        history__in=care_qs_all, created_at__gte=start_datetime, created_at__lte=end_datetime
    ).aggregate(t=Coalesce(Sum("amount"), ZERO, output_field=DECIMAL))["t"]

    paid_agreements = Payment.objects.filter(
        agreement__isnull=False, created_at__gte=start_datetime, created_at__lte=end_datetime
    ).aggregate(t=Coalesce(Sum("amount"), ZERO, output_field=DECIMAL))["t"]

    total_paid = (paid_histories or Decimal("0")) + (paid_agreements or Decimal("0"))

    outstanding = total_billed - total_paid
    if outstanding < 0:
        outstanding = Decimal("0.00")

    # LISTA
    histories_and_agreements = []
    for h in care_qs_all:
        h.obj_type = "history"
        h.amount_display = h.amount or Decimal("0.00")
        h.debt_sum = max(h.amount_display - (h.paid_sum or Decimal("0.00")), Decimal("0.00"))
        if h.amount_display > 0:
            histories_and_agreements.append(h)

    for a in agreements_qs:
        a.obj_type = "agreement"
        a.amount_display = a.total_amount or Decimal("0.00")
        a.debt_sum = max((a.total_amount or Decimal("0.00")) - (a.paid_sum or Decimal("0.00")), Decimal("0.00"))
        histories_and_agreements.append(a)

    payments_for_agreements = Payment.objects.filter(
        created_at__gte=start_datetime, created_at__lte=end_datetime, agreement__isnull=False
    ).select_related("agreement", "patient")

    for p in payments_for_agreements:
        p.obj_type = "payment_agreement"
        p.amount_display = p.amount or Decimal("0.00")
        p.debt_sum = Decimal("0.00")
        histories_and_agreements.append(p)

    histories_and_agreements.sort(
        key=lambda x: (_obj_date(x), getattr(x, "id", 0)), reverse=(order == "desc")
    )

    return render(request, "clinic/reports_new.html", {
        "total_billed": total_billed,
        "total_paid": total_paid,
        "outstanding": outstanding,
        "histories_and_agreements": histories_and_agreements,
        "payments_by_doctor": payments_by_doctor,
        "payments_by_doctor_total": payments_by_doctor_total,
        "start_date": start_date,
        "end_date": end_date,
        "mode": mode,
        "picked_day": picked_day,
        "picked_week": picked_week,
        "picked_month": picked_month,
        "picked_year": picked_year,
        "years": range(2020, datetime.now().year + 2),
        "order": order,
    })


# ---------------- AGREEMENT CREATE ----------------
@login_required
def agreement_create(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        title = request.POST.get("title") or "Marrëveshje trajtimi"
        total_amount = Decimal(request.POST.get("total_amount") or "0")
        notes = request.POST.get("notes") or ""
        start_date = request.POST.get("start_date") or None
        end_date = request.POST.get("end_date") or None
        doctor = request.POST.get("doctor") or None  # Doktori

        Agreement.objects.create(
            patient=patient,
            title=title,
            total_amount=total_amount,
            notes=notes,
            status=request.POST.get("status", "active"),
            start_date=start_date or datetime.now().date(),
            end_date=end_date,
            doctor=doctor,  # ruhet doktori
            created_by=request.user,
            updated_by=request.user,
        )
        messages.success(request, f"Marrëveshja për {patient.emri_mbiemri} u krijua me sukses.")
        return redirect("patient_detail", pk=patient.pk)

    return render(request, "clinic/agreement_form.html", {"patient": patient})


@login_required
def upload_document(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST" and request.FILES.get("document"):
        PatientDocument.objects.create(
            patient=patient,
            file=request.FILES["document"],
            uploaded_by=request.user
        )
    return redirect("patient_detail", pk=pk)


@login_required
def delete_patient_document(request, pk):
    doc = get_object_or_404(PatientDocument, pk=pk)
    patient_id = doc.patient.id
    if request.method == "POST":
        doc.file.delete(save=False)  # fshin file nga media/
        doc.delete()
    return redirect("patient_detail", pk=patient_id)



@login_required
def checkout(request):
    patient = None
    histories = []
    agreements = []
    payments = []
    total_billed = total_paid = debt = Decimal("0.00")

    DECIMAL = DecimalField(max_digits=18, decimal_places=2)
    ZERO = Decimal("0.00")

    patient_id = request.GET.get("patient")
    if patient_id:
        patient = get_object_or_404(Patient, pk=patient_id)

        # Pagesat ekzistuese
        payments = Payment.objects.filter(patient=patient).order_by("-created_at")

        total_paid = payments.aggregate(
            s=Coalesce(Sum("amount", output_field=DECIMAL), ZERO)
        )["s"] or Decimal("0.00")

        # Histori të pacientit
        histories = (
            CareHistory.objects
            .filter(patient=patient, agreement__isnull=True, included_in_agreement=False)
            .annotate(
                paid_sum=Coalesce(Sum("payments__amount", output_field=DECIMAL), ZERO),
                debt_sum=F("amount") - Coalesce(Sum("payments__amount", output_field=DECIMAL), ZERO),
            )
            .order_by("date")
        )

        # Marrëveshje aktive
        agreements = (
            Agreement.objects
            .filter(patient=patient, status="active")
            .annotate(
                paid_sum=Coalesce(Sum("payments__amount", output_field=DECIMAL), ZERO),
                debt_sum=F("total_amount") - Coalesce(Sum("payments__amount", output_field=DECIMAL), ZERO),
            )
            .order_by("-created_at")
        )

        # Totali i faturuar
        total_billed = (
            (CareHistory.objects.filter(patient=patient).aggregate(
                s=Coalesce(Sum("amount", output_field=DECIMAL), ZERO)
            )["s"] or Decimal("0.00"))
            + (Agreement.objects.filter(patient=patient).aggregate(
                s=Coalesce(Sum("total_amount", output_field=DECIMAL), ZERO)
            )["s"] or Decimal("0.00"))
        )

        debt = max(total_billed - total_paid, Decimal("0.00"))

    # POST – krijo pagesë
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        amount = Decimal(request.POST.get("amount") or "0")
        method = request.POST.get("method") or "cash"
        notes  = request.POST.get("notes") or ""

        history_ids = request.POST.getlist("history_ids")
        agreement_id = request.POST.get("agreement_id")

        patient = get_object_or_404(Patient, pk=patient_id)

        if amount <= 0:
            messages.error(request, "Shuma nuk është e vlefshme.")
            return redirect(f"/checkout/?patient={patient.id}")

        if agreement_id and history_ids:
            messages.error(request, "Zgjidh ose marrëveshje, ose histori – jo të dyja.")
            return redirect(f"/checkout/?patient={patient.id}")

        # Pagesë për marrëveshje
        if agreement_id:
            agreement = get_object_or_404(Agreement, pk=agreement_id, patient=patient)
            Payment.objects.create(
                patient=patient,
                amount=amount,
                method=method,
                notes=notes,
                agreement=agreement,
                created_by=request.user,
            )
            messages.success(request, f"Pagesa {amount}€ u shtua për marrëveshjen {agreement.title}.")
            return redirect(f"/checkout/?patient={patient.id}")

        # Pagesë për histori
        if history_ids:
            for hid in history_ids:
                h = CareHistory.objects.filter(id=hid, patient=patient).first()
                if h:
                    Payment.objects.create(
                        patient=patient,
                        amount=amount,
                        method=method,
                        notes=notes,
                        history=h,
                        created_by=request.user,
                    )
            messages.success(request, f"Pagesa {amount}€ u shtua për {len(history_ids)} histori.")
            return redirect(f"/checkout/?patient={patient.id}")

        messages.error(request, "Zgjidh një histori ose marrëveshje për të kryer pagesën.")
        return redirect(f"/checkout/?patient={patient.id}")

    return render(request, "clinic/checkout.html", {
        "patient": patient,
        "histories": histories,
        "agreements": agreements,
        "payments": payments,
        "total_billed": total_billed,
        "total_paid": total_paid,
        "debt": debt,
    })


# 🔹 API për autocomplete të pacientëve
@login_required
def search_patients(request):
    q = request.GET.get("q", "")
    patients = Patient.objects.filter(
        Q(emri_mbiemri__icontains=q) | Q(telefoni__icontains=q)
    ).values("id", "emri_mbiemri", "telefoni")[:10]
    return JsonResponse(list(patients), safe=False)

@login_required
def user_logout(request):
    if request.method in ["POST", "GET"]:
        logout(request)
    return redirect("login")
