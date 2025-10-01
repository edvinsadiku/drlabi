# Django aplikacioni për bazën `h205760_admin_labi`

Ky projekt lidhet drejtpërdrejt me bazën ekzistuese MySQL (dump nga phpMyAdmin)
dhe ekspozon të gjitha tabelat kryesore për lexim/shkrim pa ndryshuar skemën.

## 1) Installim

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Konfigurimi i DB
Vendos variablat e mjedisit (ose modifiko `dental_records/settings.py`):

```bash
export DB_NAME=h205760_admin_labi
export DB_USER=root
export DB_PASSWORD=
export DB_HOST=127.0.0.1
export DB_PORT=3306
```

## 3) Importimi i dump-it (nëse nuk e ke në MySQL)
```bash
mysql -u$DB_USER -p$DB_PASSWORD -h $DB_HOST -P $DB_PORT $DB_NAME < h205760_admin_labi.sql
```

> **Shënim:** Modelet përdorin `managed=False` në mënyrë që Django **të mos** prekë tabelat ekzistuese.

## 4) Start
```bash
python manage.py runserver
```
Hap: http://127.0.0.1:8000 dhe shiko listën e pacientëve. Admini është aktiv: `/admin/`.

## 5) Çfarë përfshihet
- Modelet: `Patient`, `Historia`, `PatienOrtodentics`, `HistoryOrtodentics`, `Shpenzimet`, `LegacyUser`, `PasswordReset`.
- Relacione:
  - `historias.id_pacienti` → `patients.id`
  - `history_ortodentics.id_pacienti` → `patients.id`
- Admin & Views bazë për listim dhe detaje pacienti (me totat vlera/paguar/borgji).

